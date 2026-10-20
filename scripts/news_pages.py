"""Small metadata-only adapter for Xinhua's public politics section."""
import hashlib
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from scripts.update_news import excerpt, feed_date


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.meta={};self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'): self.links.append(attrs['href'])
        if tag=='meta': self.meta[(attrs.get('name') or attrs.get('property') or '').lower()]=attrs.get('content','')
        if tag=='title': self.in_title=True
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
    def handle_data(self,value):
        if self.in_title: self.title.append(value)


def read_page(url):
    req=urllib.request.Request(url,headers={'User-Agent':'LarryToday/2.0 (public metadata reader)'})
    with urllib.request.urlopen(req,timeout=20) as response:
        if urlsplit(response.url).hostname!='www.news.cn': raise ValueError('Unexpected article host')
        raw=response.read(2_000_001)
    if len(raw)>2_000_000: raise ValueError('Page too large')
    return raw.decode('utf-8')


def article_links(html,base,limit=8):
    page=Page();page.feed(html)
    urls={urljoin(base,u) for u in page.links}
    urls=[u for u in urls if urlsplit(u).hostname=='www.news.cn' and
          re.fullmatch(r'/politics/\d{8}/[a-f0-9]{32}/c\.html',urlsplit(u).path)]
    # Avoid old pinned stories at the top of the section. Bound requests per run.
    return sorted(urls,key=lambda u:(re.search(r'/politics/(\d{8})/',u)[1],u),reverse=True)[:limit]


def parse_article(html,url):
    page=Page();page.feed(html)
    day=page.meta.get('publishdate','')
    time=re.search(r'class=[\"\x27]time[\"\x27][^>]*>\s*(\d{2}:\d{2}:\d{2})\s*<',html)
    # The Chinese domestic article header uses Beijing time, not the machine timezone.
    date,_=feed_date(day+'T'+time[1]+'+08:00') if time else (None,None)
    title=re.sub(r'\s+',' ',' '.join(page.title)).strip()
    title=re.sub(r'[-_](新华网|新华网客户端)$','',title).strip()
    if not title or not date: raise ValueError('Missing publication header')
    row={'id':hashlib.sha256(url.encode()).hexdigest()[:16],'url':url,'title':title,
         'source_id':'xinhua','category':'国际政治','published_at':date,'date_precision':'timestamp',
         'date_basis':'article_header_beijing_time','feed_excerpt':excerpt(page.meta.get('description','')),
         'summary':'','verification':'官网文章元数据 · 尚未交叉核验','attribution':page.meta.get('source','')}
    if page.meta.get('source','') in ('新华社','新华网'): row['upstream_agency']='新华社'
    return row


def collect_page(feed):
    from scripts.collect import error_details
    links=article_links(read_page(feed['url']),feed['url'],feed.get('max_items',8))
    if not links: raise ValueError('No article links')
    rows=[];errors=[]
    for url in links:
        try: rows.append(parse_article(read_page(url),url))
        except Exception as error: errors.append({'url':url,**error_details(error)})
    if not rows: raise ValueError('No valid article metadata')
    return rows,errors
