"""Bounded official X timeline ingestion, with explicit identity and error states."""
import json
import re
import urllib.request
from urllib.parse import urlencode
from datetime import datetime, timezone, timedelta

from scripts.collect import error_details
from scripts.editorial import timestamp


def fetch_accounts(config, token, opener, checkpoints):
    posts=[]; results=[]; updates=dict(checkpoints)
    for account in config.get('accounts',[]):
        username=account.get('username','')
        result={'username':username,'count':0,'state':'disabled'}
        results.append(result)
        if account.get('enabled',True) is False: continue
        if account.get('identity_status') not in ('official_site_linked','manually_verified'):
            result['state']='identity_required';continue
        if not token:
            result['state']='credentials_required';continue
        try:
            if not re.fullmatch(r'[A-Za-z0-9_]{1,15}',username): raise ValueError('Invalid username')
            def request(path):
                req=urllib.request.Request('https://api.x.com/2/'+path,headers={'Authorization':'Bearer '+token})
                with opener.open(req,timeout=20) as response:
                    raw=response.read(2_000_001)
                if len(raw)>2_000_000: raise ValueError('Response too large')
                body=json.loads(raw)
                if body.get('errors'): raise ValueError('API returned errors')
                return body
            identity=request('users/by/username/'+username)['data']
            user=str(identity['id'])
            if not user.isdigit() or identity.get('username','').lower()!=username.lower(): raise ValueError('Identity mismatch')
            if account.get('user_id') and str(account['user_id'])!=user:
                result['state']='identity_mismatch';continue
            result['user_id']=user
            params={'max_results':100,'exclude':'retweets,replies','tweet.fields':'created_at,author_id,referenced_tweets,note_tweet'}
            if checkpoints.get(user): params['since_id']=checkpoints[user]
            else: params['start_time']=(datetime.now(timezone.utc)-timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')
            collected=[];complete=False
            for _ in range(max(1,min(int(config.get('max_pages_per_account',3)),10))):
                body=request('users/'+user+'/tweets?'+urlencode(params))
                if 'data' not in body and body.get('meta',{}).get('result_count')!=0: raise ValueError('Invalid timeline')
                for post in body.get('data',[]):
                    pid=str(post.get('id',''));created=timestamp(post.get('created_at'))
                    if not pid.isdigit() or not created or str(post.get('author_id'))!=user: raise ValueError('Invalid post')
                    if not (datetime.now(timezone.utc)-timedelta(days=14)<=created<=datetime.now(timezone.utc)): continue
                    collected.append({'id':'x-'+pid,'title':post.get('note_tweet',{}).get('text') or post['text'],
                        'url':'https://x.com/i/web/status/'+pid,'source_id':'x-'+user,
                        'source_name':account.get('name',username),'author_id':user,'username':username,
                        'category':'科技与 AI','published_at':created.isoformat(),'content_type':'观点',
                        'section':'业界声音','verification':'社交平台原始发言 · 未独立核验',
                        'identity_status':account['identity_status'],'referenced_tweets':post.get('referenced_tweets',[])})
                nxt=body.get('meta',{}).get('next_token')
                if not nxt: complete=True;break
                params['pagination_token']=nxt
            posts.extend(collected)
            result.update(count=len(collected),state=('available' if collected else 'empty') if complete else 'coverage_limited')
            # Advance only after all pages succeed, otherwise retry from the old checkpoint.
            if complete and collected: updates[user]=str(max(int(p['id'][2:]) for p in collected))
        except Exception as error:
            details=error_details(error)
            state={401:'unauthorized',402:'billing_required',403:'forbidden',404:'not_found',429:'rate_limited'}.get(details['http_status'],'unavailable')
            result.update(state=state,**details)
    return posts,results,updates
