"""Bounded source discovery, never automated truth verification. No LLM calls.
Search results are leads only; only relevant, retrievable primary pages are displayed.
"""
import hashlib
import ipaddress
import json
import re
import socket
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.event_graph import tokens
from scripts.update_news import atomic_json

class Page(HTMLParser):
    def __init__(self):super().__init__();self.title=[];self.body=[];self.links=[];self.in_title=False;self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','nav','footer'):self.skip+=1
        if tag=='title':self.in_title=True
        if tag=='a':self.links.extend(v for k,v in attrs if k=='href' and v)
    def handle_endtag(self,tag):
        if tag in ('script','style','nav','footer'):self.skip=max(0,self.skip-1)
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if not self.skip and data.strip():self.body.append(data.strip())

def public_url(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443):raise ValueError('unsupported_url')
    addresses=socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):raise ValueError('nonpublic_address')
    return url

class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        public_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch(url):
    public_url(url)
    req=urllib.request.Request(url,headers={'User-Agent':'LarryToday/1.0 (source discovery; public pages only)'})
    with urllib.request.build_opener(Redirect()).open(req,timeout=6) as response:
        if 'html' not in response.headers.get('Content-Type','') and 'xml' not in response.headers.get('Content-Type',''):raise ValueError('unsupported_content')
        return response.read(500_000).decode('utf-8',errors='replace'),response.url

def publisher(url,publishers):
    host=(urllib.parse.urlsplit(url).hostname or '').lower()
    return next((p['name'] for p in publishers for domain in p['domains'] if host==domain or host.endswith('.'+domain)),None)

def relevant(row,title):
    # A company name alone cannot establish that this is the same incident.
    shared=tokens(row)&tokens({'title':title})
    return len(shared)>=4 and any(len(t)>3 or re.search('[\u4e00-\u9fff]',t) for t in shared)

def search_headline(members,fallback):
    def usable(row):
        title=row.get('title_en') or row.get('title') or ''
        return not re.search(r'^(commentary|opinion|analysis|editorial)\s*:|[?？]',title,re.I)
    row=next((r for r in members if usable(r) and re.search('[a-zA-Z]',r.get('title_en') or r.get('title',''))),next((r for r in members if usable(r)),fallback))
    return row

def query_terms(row):
    title=row.get('title_en') or row.get('title') or row.get('title_zh','')
    words=re.findall(r"[A-Za-z][A-Za-z'-]*",title)
    if len(words)<4:return title[:80]
    stop=set('the a an to in of for on and with as from it its his her at by that this says said after about'.split())
    return ' '.join(w for w in words if w.lower() not in stop)[:110]

def shortlist(edition,limit=3):
    by_id={r['id']:r for r in edition.get('articles',[])}
    featured={b.get('article_id') for b in edition.get('briefing',[])}
    choices=[]
    for event in edition.get('events',[]):
        members=[by_id[i] for i in event['article_ids'] if i in by_id]
        if not members:continue
        families={r.get('publisher_family') or r.get('source_id') for r in members}
        score=min(len(families),8)*3+min(len(members),12)+8*bool(featured&set(event['article_ids']))
        if len(families)<2 and not featured&set(event['article_ids']):continue
        choices.append((score,event,members))
    choices.sort(key=lambda x:(-x[0],x[1]['id']))
    return choices[:limit]

def discover(edition,publishers,fetcher=fetch,limit=3):
    result={'date':edition['date'],'checked_at':datetime.now(timezone.utc).isoformat(),'method':'primary-source-discovery-v1','events':[],'requests':0}
    rows=edition.get('articles',[])
    for score,event,members in shortlist(edition,limit):
        lead=search_headline(members,next((r for r in members if r['id']==event.get('lead_id')),members[0]))
        bundle={'event_title':event.get('title') or lead.get('title_zh') or lead['title'],'article_ids':event['article_ids'],'priority_score':score,'materials':[],'searches':[],'errors':[]}
        group_text=' '.join(str(r.get(k) or '') for r in members for k in ('title','title_zh'))
        relevant_publishers=[p for p in publishers if any(a.casefold() in group_text.casefold() for a in p.get('aliases',[]))]
        candidates=[]
        # Existing official reporting is useful even if search is unavailable.
        for row in rows:
            pub=publisher(row.get('url',''),publishers)
            if pub and row.get('source_kind') in ('official','research') and relevant(lead,row.get('title','')+' '+row.get('title_zh','')):
                candidates.append(row['url'])
        # Follow citations in a small number of representative reporting pages.
        for row in members[:2]:
            try:
                result['requests']+=1;html,base=fetcher(row['url']);page=Page();page.feed(html)
                candidates.extend(urllib.parse.urljoin(base,u) for u in page.links if publisher(urllib.parse.urljoin(base,u),publishers))
            except Exception as error:bundle['errors'].append({'stage':'citations','type':type(error).__name__})
        # Public RSS search is best-effort; it is not a verification authority.
        headline=query_terms(lead)
        queries=['site:'+p['domains'][0]+' '+headline[:140] for p in relevant_publishers[:1]]
        queries.append(headline[:140]+' official statement')
        for query in queries:
            search={'query':query,'provider':'Bing RSS','status':'pending'};bundle['searches'].append(search)
            try:
                result['requests']+=1;xml,_=fetcher('https://www.bing.com/search?format=rss&q='+urllib.parse.quote(query))
                items=ET.fromstring(xml).findall('.//item');search['status']='completed';search['results']=len(items)
                for item in items:
                    url=item.findtext('link','')
                    if publisher(url,publishers):candidates.append(url)
            except Exception as error:search['status']='unavailable';bundle['errors'].append({'stage':'search','type':type(error).__name__})
        for url in list(dict.fromkeys(candidates))[:4]:
            try:
                result['requests']+=1;html,final=fetcher(url);pub=publisher(final,publishers)
                if not pub:continue
                page=Page();page.feed(html);title=' '.join(page.title).strip();body=' '.join(page.body)
                if not title or not relevant(lead,title):continue
                # Excerpts come only from the downloaded page, never search summaries or AI.
                sentences=re.split(r'(?<=[.!?。])\s+',body)
                excerpt=next((s for s in sentences if 40<=len(s)<=400 and relevant(lead,s)), '')
                bundle['materials'].append({'title':title[:240],'url':final,'publisher':pub,'kind':'机构原始材料','status':'retrieved','excerpt':excerpt[:240],'retrieved_at':result['checked_at']})
                if len(bundle['materials'])>=3:break
            except Exception as error:bundle['errors'].append({'stage':'material','type':type(error).__name__})
        bundle['status']='materials_found' if bundle['materials'] else 'retrieval_unavailable' if all(s['status']=='unavailable' for s in bundle['searches']) and len(bundle['errors'])>=len(bundle['searches'])+min(2,len(members)) else 'no_relevant_material'
        result['events'].append(bundle)
    return result

def run(root=ROOT):
    root=Path(root);edition=json.loads((root/'data/latest.json').read_text(encoding='utf-8'))
    path=root/'data/evidence'/(edition['date']+'.json')
    if path.exists():
        old=json.loads(path.read_text(encoding='utf-8'))
        if old.get('attempts',1)>=2 or not any(e.get('status')=='retrieval_unavailable' for e in old.get('events',[])):return {'state':'cached','date':edition['date']}
    else:old={} 
    publishers=json.loads((root/'config/evidence-publishers.json').read_text(encoding='utf-8-sig'))['publishers']
    # Include configured official feed domains without hand-special-casing individual events.
    feeds=json.loads((root/'config/feeds.json').read_text(encoding='utf-8'))
    for f in feeds:
        if f.get('kind') in ('official','research'):
            domain=urllib.parse.urlsplit(f['url']).hostname
            if domain and not publisher(f['url'],publishers):publishers.append({'name':f['name'],'domains':[domain],'aliases':[f['name']]})
    value=discover(edition,publishers);value['attempts']=old.get('attempts',0)+1;atomic_json(path,value)
    return {'state':'completed','date':edition['date'],'events':len(value['events']),'materials':sum(len(e['materials']) for e in value['events']),'requests':value['requests']}

if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
