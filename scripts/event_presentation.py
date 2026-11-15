"""Deterministic, attributed editorial views. No API calls or invented facts."""
import hashlib
import re
from collections import Counter
from scripts.newsroom import IMPACT, material, FALLBACK


def summary(row):
    return row.get('summary_zh') or row.get('feed_excerpt') or row.get('title_zh') or row.get('title', '')


def attributed(row, text=None):
    return {'text': text or summary(row), 'article_id': row['id'],
            'source': row.get('source_name') or row['source_id'], 'url': row.get('url', '')}


def claims(rows):
    """Extract attributed statements, never infer that disagreement proves falsity."""
    result=[]; seen=set()
    for row in rows:
        for sentence in re.split(r'(?<=[。！？])|(?<=\.)\s+', summary(row)):
            if not re.search(r'表示|声称|指控|否认|反驳|承认|称|\b(says?|claims?|denies|denied|alleges?)\b', sentence, re.I):continue
            if sentence in seen:continue
            seen.add(sentence)
            kind='回应与否认' if re.search(r'否认|反驳|\b(denies|denied|rejects)\b',sentence,re.I) else '报道中的说法'
            result.append(dict(attributed(row,sentence),kind=kind))
            if len(result)==4:return result
    return result


def enrich(events, rows, tracks):
    by_id={r['id']:r for r in rows}
    for event in events:
        lead=by_id[event['lead_id']]; members=[by_id[i] for i in event['article_ids']]
        headline,_=material(lead)
        impact,reason=max(((w,label) for w,label,p in IMPACT if re.search(p,headline,re.I)),default=(1,'本期社会与行业观察'))
        if re.search(r'全国.{0,8}(停飞|断电)|全球.{0,8}(故障|中断)|\b(nationwide ground stop|global outage)\b',headline,re.I):impact,reason=8,'重大基础设施与公共服务中断'
        if re.search(r'二战|一战|周年|纪念|\b(world war|anniversary|remnants)\b',headline,re.I):impact=min(impact,1)
        if lead.get('content_type') in ('评论','观点','评测') or lead.get('research_status')=='preprint':impact-=3
        if re.search(r'桌游|星座|优惠|周年|\b(quiz|shopping|anniversary|board game)\b',headline,re.I):impact-=4
        families={r.get('upstream_agency') or r.get('publisher_family') or r['source_id'] for r in members}
        if lead.get('research_status')=='preprint' or 'arxiv.org/' in lead.get('url',''):impact=min(impact,0)
        picks=[r.get('editorial_pick') or {} for r in members]
        pick=min((p for p in picks if p.get('basis')=='ai_shortlist' and isinstance(p.get('order'),int)),key=lambda p:p['order'],default={})
        bonus=max(0,12-pick.get('order',12)) if pick.get('basis')=='ai_shortlist' and isinstance(pick.get('order'),int) else 0
        progress=bool(re.search(r'获批|生效|达成|宣布|判决|辞职|签署|\b(approves|signs|resigns|verdict|agreement)\b',headline,re.I))
        event['priority']={'score':impact*3+min(len(families)-1,4)*2+3*progress+bonus,
                           'reason':pick.get('reason') or reason,'independent_sources':len(families),'new_development':progress}
        first=tracks[event['story_id']]['timeline'][0]['reports'][-1]
        event['guide']={'origin':attributed(first),'latest':attributed(lead),
                        'importance':pick.get('reason') or reason,
                        'importance_basis':'编辑选题依据', 'claims':claims(members)}
    events.sort(key=lambda e:(-e['priority']['score'],e['id']))
    # A small, diverse front page; continued stories with major changes can still lead.
    counts=Counter(); main=[]
    for event in events:
        if len(main)<5 and counts[event['category']]<2 and event['priority']['score']>=12:
            main.append(event['id']);counts[event['category']]+=1
    for event in events:
        event['editorial_section']='今日主线' if event['id'] in main else '持续进展' if event['reporting_days']>1 else '值得关注'
    order={'今日主线':0,'值得关注':1,'持续进展':2}
    events.sort(key=lambda e:(order[e['editorial_section']],-e['priority']['score'],e['id']))
    return events


def topic_view(events, rows, named):
    by_id={r['id']:r for r in rows}; topics={}
    for event in events:
        # Named long-running topics plus repeated concrete editorial tags.
        values={named(by_id[i]) for i in event['article_ids']} - {None}
        for key,label in values:
            topic=topics.setdefault(key,{'id':key,'title':label,'event_ids':[]})
            topic['event_ids'].append(event['id'])
    # Other subjects can form dossiers without pretending that they are one event.
    tags={}
    for event in events:
        for tag in set(by_id[event['lead_id']].get('tags',[])[:3]):
            if len(tag)>=2 and tag not in FALLBACK.values():tags.setdefault(tag,[]).append(event['id'])
    for label,ids in tags.items():
        if 3<=len(ids)<=40:
            key='topic-'+hashlib.sha256(label.encode()).hexdigest()[:12]
            topics[key]={'id':key,'title':label,'event_ids':ids}
    values=sorted(topics.values(),key=lambda t:(-len(t['event_ids']),t['id']))[:16]
    for event in events:
        event['topics']=[{'id':t['id'],'title':t['title']} for t in values if event['id'] in t['event_ids']][:3]
    return values
