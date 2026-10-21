"""Daily boundaries, conservative event grouping and diverse editorial selection."""
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import re

SHANGHAI=timezone(timedelta(hours=8))
CATEGORIES=['国际政治','科技与 AI','经济与投资','科学与探索','环境与气候','社会与文化']

def timestamp(value):
    try:
        d=datetime.fromisoformat(value.replace('Z','+00:00'))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (ValueError,TypeError,AttributeError): return None

def window(now=None, day=None):
    now=now or datetime.now(timezone.utc)
    local=now.astimezone(SHANGHAI)
    end=datetime.fromisoformat(day).replace(hour=7,tzinfo=SHANGHAI) if day else local.replace(hour=7,minute=0,second=0,microsecond=0)
    if not day and end>local: end-=timedelta(days=1)
    if end>now: raise ValueError('晨报截稿时间尚未到达；请在北京时间 07:00 后发布该期')
    return {'start':(end-timedelta(days=1)).isoformat(),'end':end.isoformat(),'timezone':'Asia/Shanghai','date':end.date().isoformat()}

def classify(row):
    from scripts.geography import geography
    row['geography']=geography(row)
    text=' '.join(str(row.get(k,'')) for k in ('title','title_zh','title_en','feed_excerpt')).lower()
    row.setdefault('original_category',row['category'])
    rules=[('科技与 AI',r'\b(ai|artificial intelligence|openai|anthropic|semiconductor|cybersecurity|llm)\b|人工智能|大模型|芯片'),('环境与气候',r'\b(climate|emissions|renewable|biodiversity)\b|气候|碳排放'),('科学与探索',r'\b(nasa|astronomy|spacecraft|clinical trial)\b|航天|天文学'),('经济与投资',r'\b(inflation|interest rates|stock market|central bank|gdp)\b|通胀|央行|经济增长')]
    for category,pattern in rules:
        if re.search(pattern,text): row['category']=category;break
    # Explicit publisher section paths override broad cross-topic keyword matches.
    path=row['url'].lower()
    if re.search(r'/(deportes|sports?|culture|cultura|television|arts)/',path): row['category']='社会与文化'
    elif re.search(r'/(environment|climate)/',path): row['category']='环境与气候'
    elif re.search(r'/(economy|economia|business)/',path): row['category']='经济与投资'
    title=row['title'].lower()
    row['content_type']='研究' if row.get('source_kind')=='research' else '公告' if row.get('source_kind')=='official' else '新闻'
    if re.search(r'\breview\b|评测|剧评|影评',title): row['content_type']='评测'
    elif re.search(r'\b(opinion|editorial)\b|/commentisfree/|观点|社论',title+' '+row['url']): row['content_type']='评论'
    elif re.search(r'\b(best .{0,35}(gifts|deals|toys)|shopping|discount)\b|购物推荐|优惠券',title): row['content_type']='消费推荐'
    if row.get('research_status')=='preprint': row['content_type']='预印本修订' if row.get('announcement_type') in ('replace','replace-cross') else '预印本'
    elif row.get('source_kind')=='opinion': row['content_type']='观点'
    return row

def partition(rows, bounds):
    start,end=timestamp(bounds['start']),timestamp(bounds['end'])
    main,background,excluded=[],[],Counter()
    for row in rows:
        classify(row)
        d=timestamp(row.get('published_at'))
        if not d: excluded['unknown_date']+=1;continue
        if row['content_type']=='消费推荐': excluded['shopping']+=1;continue
        if start<=d<end:
            row['section']='本期新闻';main.append(row)
        elif start-timedelta(days=7)<=d<start:
            row['section']='背景阅读';background.append(row)
        else: excluded['outside_window']+=1
    return main,background,dict(excluded)

def rank(row):
    text=(row.get('title','')+' '+row.get('title_zh','')).lower()
    score=1
    if row.get('content_type') in ('新闻','公告','研究'): score+=2
    if re.search(r'\b(election|war|ceasefire|earthquake|rate|breakthrough|launch)\b|选举|战争|停火|地震|利率|发布|突破',text): score+=2
    if row.get('source_kind') in ('official','research'): score+=1
    return score

def diverse(rows,limit):
    candidates=sorted(rows,key=lambda r:(rank(r),r.get('published_at') or ''),reverse=True)
    selected=[];families=Counter();categories=Counter();regions=Counter()
    while candidates and len(selected)<limit:
        # Soft source cap: repetition costs more, but scarce coverage never gets fabricated.
        best=max(candidates,key=lambda r:rank(r)-families[r.get('publisher_family',r['source_id'])]*3-categories[r['category']]*.8-regions[r.get('source_region','未知')]*.3)
        candidates.remove(best);selected.append(best)
        families[best.get('publisher_family',best['source_id'])]+=1;categories[best['category']]+=1;regions[best.get('source_region','未知')]+=1
    return selected

def events(rows,comparisons):
    by_id={r['id']:r for r in rows}; groups=[]; used=set()
    for comparison in comparisons:
        ids=comparison['article_ids']
        # Avoid transitive merging of loosely related events; evidence stays in its own section.
        if any(i not in by_id or i in used for i in ids): continue
        dates=[timestamp(by_id[i].get('published_at')) for i in ids]
        if any(d is None for d in dates) or max(dates)-min(dates)>timedelta(hours=48): continue
        if len({by_id[i].get('upstream_agency') or by_id[i].get('publisher_family',by_id[i]['source_id']) for i in ids})<2: continue
        lead=diverse([by_id[i] for i in ids],1)[0]
        groups.append({'id':'event-'+hashlib.sha256('|'.join(sorted(ids)).encode()).hexdigest()[:12],'lead_id':lead['id'],'article_ids':ids,'category':lead['category'],'title':comparison['title_zh'],'comparison':comparison})
        used.update(ids)
    for row in rows:
        if row['id'] not in used: groups.append({'id':'event-'+row['id'],'lead_id':row['id'],'article_ids':[row['id']],'category':row['category'],'title':row.get('title_zh',row['title'])})
    groups.sort(key=lambda e:by_id[e['lead_id']].get('published_at') or '',reverse=True)
    return groups

def assemble(rows,comparisons,bounds):
    main,background,excluded=partition(rows,bounds)
    background=diverse(background,12)
    current_events=events(main,comparisons)
    by_lead={e['lead_id']:e for e in current_events}
    selected=diverse([r for r in main if r['id'] in by_lead],8)
    briefing=[{'event_id':by_lead[r['id']]['id'],'article_id':r['id'],'title':r.get('title_zh',r['title']),'summary':r.get('summary_zh') or r.get('summary') or '阅读来源原文了解详情。','category':r['category']} for r in selected]
    return {'articles':main+background,'events':current_events,'background_events':events(background,comparisons),'briefing':briefing,'window':bounds,'excluded':excluded,'coverage':{'sources':dict(Counter(r['source_id'] for r in main)),'regions':dict(Counter(r.get('source_region','未知') for r in main))},'reading_minutes':max(1,round(sum(len(r.get('summary_zh',''))+len(r.get('title_zh',r['title'])) for r in main)/450))}
