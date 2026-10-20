"""RSS ingestion and manual edition publishing. Python standard library only."""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

class FeedText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.hidden=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.hidden+=1
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.hidden=max(0,self.hidden-1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def excerpt(html):
    parser=FeedText(); parser.feed(html)
    return re.sub(r'\s+',' ',' '.join(parser.parts)).strip()[:1800]
FEEDS = [('guardian','国际政治','https://www.theguardian.com/world/rss'), ('bbc','国际政治','https://feeds.bbci.co.uk/news/world/rss.xml'), ('france24','国际政治','https://www.france24.com/en/rss'), ('fed','经济与投资','https://www.federalreserve.gov/feeds/press_all.xml'), ('nasa','科学与探索','https://www.nasa.gov/feed/')]
FEEDS += [('guardian','科技与 AI','https://www.theguardian.com/technology/rss'), ('guardian','经济与投资','https://www.theguardian.com/business/rss'), ('guardian','环境与气候','https://www.theguardian.com/environment/rss'), ('guardian','社会与文化','https://www.theguardian.com/culture/rss')]

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def safe_url(url):
    from urllib.parse import urlsplit
    p = urlsplit(url)
    return p.scheme in ('https','http') and bool(p.hostname) and not p.username

def feed_date(value):
    """Preserve date precision; updated timestamps are never publication dates."""
    value=value.strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        try: return None,datetime.fromisoformat(value).date().isoformat()
        except ValueError: return None,None
    try:
        d=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:
        try: d=parsedate_to_datetime(value)
        except (TypeError,ValueError,OverflowError): return None,None
    return (d.astimezone(timezone.utc).isoformat(),None) if d.tzinfo else (None,None)

def parse_feed(payload, source, category, limit=24):
    if b'<!DOCTYPE' in payload.upper() or b'<!ENTITY' in payload.upper():
        raise ValueError('XML entities are not supported')
    root = ET.fromstring(payload)
    rows = []
    items=root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry') or root.findall('.//{http://purl.org/rss/1.0/}item')
    for item in items[:limit]:
        original=item
        # Normalize Atom and RSS 1.0 into the RSS 2.0 fields consumed below.
        if item.tag!='item':
            normalized=ET.Element('item')
            fields={'title':'title','link':'link','published':'pubDate','date':'pubDate','summary':'description','description':'description','encoded':'description'}
            for child in item:
                name=child.tag.rsplit('}',1)[-1]
                if name in fields:
                    key=fields[name]
                    if normalized.find(key) is not None: continue
                    value=child.get('href','') if name=='link' and child.get('href') else child.text or ''
                    if name=='link' and child.get('rel','alternate')!='alternate': continue
                    ET.SubElement(normalized,key).text=value
            item=normalized
        title = re.sub(r'\s+', ' ', item.findtext('title', '')).strip()
        url = item.findtext('link','').strip()
        if not title or not safe_url(url): continue
        raw_date=item.findtext('pubDate','') or item.findtext('{http://purl.org/dc/elements/1.1/}date','')
        date,day=feed_date(raw_date)
        rows.append({'id':hashlib.sha256(url.encode()).hexdigest()[:16], 'title':title, 'url':url, 'source_id':source, 'category':category, 'published_at':date, 'feed_excerpt':excerpt(item.findtext('description','')), 'summary':'', 'verification':'来源报道 · 尚未交叉核验'})
        row=rows[-1]
        if day: row['published_day']=day
        row['date_precision']='timestamp' if date else 'day' if day else 'unknown'
        atom='{http://www.w3.org/2005/Atom}'
        updated=original.findtext(atom+'updated','')
        if updated: row['updated_at']=feed_date(updated)[0]
        authors=[a.findtext(atom+'name','').strip() for a in original.findall(atom+'author')]
        authors += [excerpt(c.text or '') for c in original if c.tag.rsplit('}',1)[-1] in ('creator','author') and c.text and c.text.strip()]
        if authors: row['authors']=list(dict.fromkeys(a for a in authors if a))
        doi=original.findtext('{http://arxiv.org/schemas/atom}doi','') or original.findtext('{http://prismstandard.org/namespaces/basic/2.0/}doi','')
        if doi: row['doi']=doi.strip()
        if source=='arxiv':
            fields={c.tag.rsplit('}',1)[-1]:c.text or '' for c in original}
            if fields.get('DOI'): row['doi']=fields['DOI'].strip()
            if fields.get('journal_reference'): row['journal_reference']=fields['journal_reference'].strip()
            match=re.search(r'arxiv\.org/abs/([^?#]+)',url)
            if match:
                row['paper_id']=re.sub(r'v\d+$','',match[1])
                row['url']='https://arxiv.org/abs/'+match[1]
                row['id']=hashlib.sha256(row['url'].encode()).hexdigest()[:16]
            row.update(research_status='preprint',verification='预印本 · 此版本未经同行评审核验',source_kind='research')
            announcement=re.search(r'Announce Type:\s*([\w-]+)',row['feed_excerpt'])
            if announcement or fields.get('announce_type'):
                row['announcement_type']=fields.get('announce_type') or announcement[1]
                row['date_basis']='rss_announcement'
            else: row['date_basis']='first_submission' if original.tag==atom+'entry' else 'feed_publication'
            version=re.search(r'arXiv:\S+v(\d+)',row['feed_excerpt'])
            if version: row['paper_version']=int(version[1])
        credit=original.findtext('source','')+' '+' '.join(row.get('authors',[]))
        for agency in ('Reuters','Associated Press','AFP','新华社'):
            if agency.lower() in credit.lower(): rows[-1]['upstream_agency']=agency;break
    return rows

def validate_articles(rows):
    if not isinstance(rows, list) or not rows: raise ValueError('articles 必须是非空数组')
    clean = []
    for row in rows:
        if not isinstance(row, dict): raise ValueError('文章必须是对象')
        for key in ('title','url','source_id','category'):
            if not isinstance(row.get(key), str) or not row[key].strip(): raise ValueError('缺少字段: '+key)
        if not safe_url(row['url']): raise ValueError('原文链接必须是 HTTP(S) URL')
        if row.get('published_at'):
            d = datetime.fromisoformat(row['published_at'].replace('Z','+00:00'))
            if not d.tzinfo: raise ValueError('published_at 必须包含时区')
        if not isinstance(row.get('summary',''), str): raise ValueError('summary 必须是文本')
        clean.append({**row, 'id':hashlib.sha256(row['url'].encode()).hexdigest()[:16], 'verification':'来源报道 · 尚未交叉核验'})
    return clean

def publish(manual=None, ai=True, ai_limit=None, existing=False, edition_date=None, revision_note=None):
    DATA.mkdir(exist_ok=True)
    lock = DATA / '.update.lock'
    try: fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError: raise RuntimeError('已有更新任务运行；异常退出后请确认无任务再删除 data/.update.lock')
    os.close(fd)
    try:
        rows, statuses = [], []
        previous=None
        if existing:
            previous=json.loads((DATA/'latest.json').read_text(encoding='utf-8'))
            rows=previous['articles']
            statuses=previous.get('sources_status',[])
        elif manual:
            value = json.loads(Path(manual).read_text(encoding='utf-8-sig'))
            rows = validate_articles(value if isinstance(value,list) else value['articles'])
            if (DATA/'source-health.json').exists(): statuses=json.loads((DATA/'source-health.json').read_text(encoding='utf-8'))
        else:
            from scripts.collect import collect,collect_social
            rows,statuses=collect(DATA)
            collect_social(DATA)
            if not any(s.get('ok') for s in statuses): raise RuntimeError('本次全部订阅失败，保留已有日报')
        now = datetime.now(timezone.utc)
        atomic_json(DATA/'last-update.json', {'attempted_at':now.isoformat(),'sources':statuses,'count':len(rows)})
        if not rows: raise RuntimeError('全部来源不可用，保留上一版。详见 data/last-update.json')
        rows = list({r['url']:r for r in rows}.values())
        rows.sort(key=lambda r:r.get('published_at') or '', reverse=True)
        from scripts.editorial import window,partition,diverse,assemble
        bounds=window(now,edition_date or (previous['date'] if previous else None))
        day=bounds['date']
        if (DATA/'editions'/f'{day}.json').exists() and not revision_note:
            raise ValueError('该期已发布；请提供 --revision-note 说明修订原因。初版不会覆盖')
        main,background,excluded=partition(rows,bounds)
        rows=main+diverse(background,12)
        if not rows: raise RuntimeError('窗口内无可用内容，保留上一期')
        comparisons=[]
        ai_status={'state':'disabled'}
        if ai:
            from scripts.ai_news import enrich
            try: rows,comparisons,ai_status=enrich(rows,DATA,ai_limit)
            except Exception as error:
                ai_status={'state':'unavailable','error_type':type(error).__name__}
                print('AI unavailable; publishing original source metadata',flush=True)
        edition = {'date':day,'updated_at':datetime.now(timezone.utc).isoformat(),'mode':'live','sources_status':statuses,'comparisons':comparisons,'ai_status':ai_status}
        edition.update(assemble(rows,comparisons,bounds))
        edition['excluded']=excluded
        from scripts.editions import save
        revision=save(DATA,edition,revision_note)
        return {'count':len(rows),'date':day,'sources':statuses,'ai':ai_status,'revision':revision}
    finally:
        lock.unlink(missing_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--import-file', help='发布人工编辑的 JSON 文章数组')
    parser.add_argument('--no-ai', action='store_true', help='仅采集，不调用 AI')
    parser.add_argument('--ai-limit', type=int, help='限制本次新处理文章数；缓存不占额度')
    parser.add_argument('--enrich-existing', action='store_true', help='处理现有日报，保留原刊期')
    parser.add_argument('--edition-date', help='刊期 YYYY-MM-DD；默认最近已到达的北京时间07:00')
    parser.add_argument('--revision-note', help='已发布刊期的修订说明；初版永久保留')
    args = parser.parse_args()
    if args.ai_limit is not None and args.ai_limit<0: parser.error('--ai-limit must be nonnegative')
    if args.enrich_existing and args.import_file: parser.error('Cannot combine import and enrich-existing')
    try: print(json.dumps(publish(args.import_file,not args.no_ai,args.ai_limit,args.enrich_existing,args.edition_date,args.revision_note), ensure_ascii=False))
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
