"""Configured RSS/Atom adapters and optional authenticated X observation pool."""
import json
import hashlib
import os
import re
import urllib.request
import urllib.error
import socket
import ssl
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]

def error_details(error):
    """Only bounded classifications: never persist credentials or response bodies."""
    reason=getattr(error,'reason',error)
    code=error.code if isinstance(error,urllib.error.HTTPError) else None
    kind=('http' if code else 'dns' if isinstance(reason,socket.gaierror) else
          'tls' if isinstance(reason,ssl.SSLError) else
          'timeout' if isinstance(reason,(TimeoutError,socket.timeout)) else
          'connection' if isinstance(error,(urllib.error.URLError,ConnectionError)) else 'parse_or_validation')
    return dict(error=type(error).__name__,error_kind=kind,http_status=code)

def expected_empty(payload, feed):
    """arXiv explicitly publishes empty RSS on non-announcement days."""
    if feed.get('source_id')!='arxiv': return False
    import xml.etree.ElementTree as ET
    root=ET.fromstring(payload)
    channel=root.find('channel')
    return root.tag=='rss' and channel is not None and not channel.findall('item')

def collect(data):
    data.mkdir(parents=True,exist_ok=True)
    lock=data/'.collect.lock'
    try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError: raise RuntimeError('已有采集任务运行，稍后重试')
    os.close(fd)
    try: return _collect(data)
    finally: lock.unlink(missing_ok=True)

def _collect(data):
    from scripts.update_news import parse_feed,atomic_json
    feeds=json.loads((ROOT/'config/feeds.json').read_text(encoding='utf-8'))
    old={}
    if (data/'source-health.json').exists():
        old={s['id']:s for s in json.loads((data/'source-health.json').read_text(encoding='utf-8'))}
    def fetch(feed):
        status={k:feed[k] for k in ('id','source_id','name','region','category','url','enabled')}
        status['checked_at']=datetime.now(timezone.utc).isoformat()
        status['last_success']=old.get(feed['id'],{}).get('last_success')
        rows=[]
        if not feed['enabled']: return rows,dict(status,ok=False,state='disabled')
        try:
            payload=b''
            if feed.get('adapter')=='xinhua_page':
                from scripts.news_pages import collect_page
                rows,errors=collect_page(feed)
                status['article_errors']=errors
            else:
                req=urllib.request.Request(feed['url'],headers={'User-Agent':'LarryToday/2.0 (public feed reader)'})
                with urllib.request.urlopen(req,timeout=20) as response: payload=response.read(2_000_001)
                if len(payload)>2_000_000: raise ValueError('Feed exceeds size limit')
                rows=parse_feed(payload,feed['source_id'],feed['category'],limit=feed.get('max_items',24))
            if not rows:
                if expected_empty(payload,feed):
                    return [],dict(status,ok=True,state='empty',count=0,last_success=status['checked_at'])
                raise ValueError('No feed entries')
            for row in rows:
                row.update(source_name=feed['name'],publisher_family=feed['family'],source_region=feed['region'],source_kind=feed['kind'])
                if feed['kind']=='opinion':
                    row.update(content_type='观点',section='业界声音',verification='作者博客/通讯 · 个人观点 · 未独立核验')
            status.update(ok=True,state='available',count=len(rows),last_success=status['checked_at'],latest_article=max((r['published_at'] for r in rows if r.get('published_at')),default=None))
            status['item_limit']=feed.get('max_items',24)
            status['limit_reached']=len(rows)>=status['item_limit']
            latest_day=max((r.get('published_day') or (r.get('published_at') or '')[:10] for r in rows),default='')
            status['latest_day']=latest_day or None
            if latest_day and (datetime.now(timezone.utc).date()-datetime.fromisoformat(latest_day).date()).days>14: status['state']='stale'
            elif not status['latest_article']: status['state']='date_only'
            if status.get('article_errors'): status['state']='partial'
        except Exception as error:
            status.update(ok=False,state='unavailable',**error_details(error))
        return rows,status
    rows=[];statuses=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        for articles,status in pool.map(fetch,feeds): rows.extend(articles);statuses.append(status)
    atomic_json(data/'source-health.json',statuses)
    # Keep successful recent metadata across feed rotations and source outages.
    previous=[]
    if (data/'article-pool.json').exists(): previous=json.loads((data/'article-pool.json').read_text(encoding='utf-8'))
    from scripts.editorial import timestamp
    now=datetime.now(timezone.utc)
    def recent(row):
        date=timestamp(row.get('published_at'))
        if date: return 0<=(now-date).total_seconds()<=14*86400
        try: return 0<=(now.date()-datetime.fromisoformat(row.get('published_day','')).date()).days<=14
        except ValueError: return False
    retained=[r for r in previous if recent(r)]
    merged={r['url']:r for r in retained}
    merged.update({r['url']:r for r in rows})
    opinions=[r for r in rows if r.get('source_kind')=='opinion']
    atomic_json(data/'opinion-posts.json',opinions)
    articles=[r for r in merged.values() if r.get('source_kind')!='opinion']
    atomic_json(data/'article-pool.json',articles)
    atomic_json(data/'background-candidates.json',[r for r in articles if r.get('published_day') and not r.get('published_at') and recent(r)])
    return articles,statuses

def collect_social(data):
    from scripts.ai_news import settings,NoRedirect
    from scripts.update_news import atomic_json
    config=json.loads((ROOT/'config/social.json').read_text(encoding='utf-8'))
    token=settings().get('X_BEARER_TOKEN','')
    status={'configured':bool(token),'enabled':config.get('enabled',False),'accounts':len(config.get('accounts',[])),'state':'disabled','checked_at':datetime.now(timezone.utc).isoformat()}
    from scripts.social import fetch_accounts
    checkpoints_path=data/'social-checkpoints.json'
    checkpoints=json.loads(checkpoints_path.read_text(encoding='utf-8')) if checkpoints_path.exists() else {}
    posts=[];updates=None
    if config.get('enabled'):
        posts,accounts,updates=fetch_accounts(config,token,urllib.request.build_opener(NoRedirect),checkpoints)
        status['account_statuses']=accounts
        failures=[a for a in accounts if a['state'] not in ('available','empty','disabled')]
        successes=[a for a in accounts if a['state'] in ('available','empty')]
        status.update(state='partial' if failures and successes else 'unavailable' if failures else 'complete' if accounts else 'accounts_required',failed_accounts=len(failures))
    else:
        status['account_statuses']=[{'username':a.get('username'),'state':'disabled','identity_status':a.get('identity_status')} for a in config.get('accounts',[])]
    opinion_path=data/'opinion-posts.json'
    if opinion_path.exists(): posts.extend(json.loads(opinion_path.read_text(encoding='utf-8')))
    status['opinion_posts']=sum(p.get('source_kind')=='opinion' for p in posts)
    atomic_json(data/'social-status.json',status)
    old=json.loads((data/'social-posts.json').read_text(encoding='utf-8')) if (data/'social-posts.json').exists() else []
    from scripts.editorial import timestamp
    merged={p['id']:p for p in old if timestamp(p.get('published_at')) and 0<=(datetime.now(timezone.utc)-timestamp(p['published_at'])).total_seconds()<=14*86400}
    merged.update({p['id']:p for p in posts if timestamp(p.get('published_at')) and 0<=(datetime.now(timezone.utc)-timestamp(p['published_at'])).total_seconds()<=14*86400})
    atomic_json(data/'social-posts.json',list(merged.values()))
    if updates is not None: atomic_json(checkpoints_path,updates)
    return status

if __name__=='__main__':
    data=ROOT/'data';data.mkdir(exist_ok=True)
    rows,status=collect(data)
    collect_social(data)
    print(json.dumps({'articles':len(rows),'sources':[{'id':s['id'],'ok':s['ok'],'count':s.get('count',0),'latest':s.get('latest_article'),'error':s.get('http_status') or s.get('error')} for s in status]},ensure_ascii=False))
