"""Evidence-preserving event views, built from published editions only.
No requests, no discarded sources, no inferred causal assertions.
"""
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from functools import lru_cache
from datetime import date, timedelta
from pathlib import Path

STOP=set('the and for with from that this after over says news new into will have been about their more than how why what are was its can could would world amid live updates latest first report reports'.split())
STOP.update('us usa united states china chinese france french britain british uk russia russian ukraine ukrainian italy italian says said announces announced approves approved passes passed'.split())
ZH_STOP=set('美国 中国 法国 英国 俄国 记者 报道 表示 新闻 今天 目前 可能 已经 一个 以及 进行 认为 相关 最新 今年 近日 全球 世界 国际'.split())
ACTION=[('election',r'选举|投票|大选|\b(election|midterms?|ballot|vote)\b'),('unrest',r'骚乱|抗议|示威|\b(riots?|protests?|unrest)\b'),('attack',r'袭击|轰炸|空袭|\b(attack|strike|bombing)\b'),('quake',r'地震|\bearthquake\b'),('policy',r'法案|立法|禁令|关税|\b(law|ban|tariff)\b'),('release',r'发布|推出|\b(launch|release|unveil)\b')]
CONNECT=re.compile(r'外溢|蔓延|波及|受.{0,20}启发|引发.{0,20}(抗议|骚乱)|spillover|spill.over|spread.{0,30}(from|to)|inspired by',re.I)

def title(row):return row.get('title_zh') or row.get('title') or ''
def text(row):return ' '.join(str(row.get(k) or '') for k in ('title_zh','title','title_en'))+' '+str((row.get('event_assignment') or {}).get('title') or '')
def event_title(row):return (row.get('event_assignment') or {}).get('title') or (named_event(row)[1] if named_event(row) else title(row))
def named_event(row):
    value=text(row)
    year=(row.get('published_at') or '')[:4]
    if not year.isdigit():return None
    if re.search(r'美国.{0,5}中期选举|\b(?:US|U.S.|American).{0,12}midterm|\bmidterm elections?\b',value,re.I) and not re.search(r'伊朗|油价|袭击|\b(oil|Iran|attack|strike)\b',value,re.I):return ('us-midterms-'+year,year+' 年美国中期选举')
    if re.search(r'伊朗战争|\bIran war\b|\bwar (?:in|with) Iran\b',value,re.I):return ('iran-war-'+year,'伊朗战争进展')
    return None

def tokens(row):
    result=lexical(text(row).lower()).copy()
    if named_event(row):result.add('@'+named_event(row)[0])
    return result

@lru_cache(maxsize=50000)
def lexical(value):
    words=set(re.findall(r'[a-z][a-z0-9-]{2,}',value))-STOP
    for run in re.findall(r'[\u4e00-\u9fff]+',value):
        words.update(run[i:i+2] for i in range(len(run)-1))
    return words-ZH_STOP

def countries(row):return set(row.get('geography',{}).get('countries',[]))

def primary_countries(row):
    from scripts.geography import PATTERNS
    return {code for code,_,pattern in PATTERNS if pattern.search(text(row))} or countries(row)
def action(row):return action_text(text(row))

@lru_cache(maxsize=50000)
def action_text(value):return {key for key,pattern in ACTION if re.search(pattern,value,re.I)}
def day_distance(a,b):return abs((date.fromisoformat(a)-date.fromisoformat(b)).days)
def family(row):return row.get('upstream_agency') or row.get('publisher_family') or row['source_id']
def identity(row):
    # Exact publisher identity is especially useful for successive arXiv versions.
    match=re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d+)',row.get('url',''))
    return 'arxiv:'+match[1] if match else None

def compatible(a,b):
    ca,cb=countries(a),countries(b)
    if ca and cb and not ca&cb:return False
    aa,ab=action(a),action(b)
    if aa and ab and not aa&ab:return False
    # Distinct papers are not one event merely because their vocabulary overlaps.
    if a.get('research_status')=='preprint' or b.get('research_status')=='preprint':
        return bool(identity(a) and identity(a)==identity(b))
    return True

def similarity(a,b,ta,tb,weights):
    if not compatible(a,b):return 0
    if identity(a) and identity(a)==identity(b):return 1
    if named_event(a) and named_event(a)==named_event(b):return 1
    shared=ta&tb
    if len(shared)<4:return 0
    weight=lambda ts:sum(weights.get(t,1) for t in ts)
    score=weight(shared)/max(1,min(weight(ta),weight(tb)))
    # At least two discriminative terms; common country/topic words alone cannot merge.
    if not shared-{'election','midterm','protest','parliament','president','government','market','model'}:return 0
    return score

def group_day(rows, legacy):
    """Complete-link against representative anchors; never transitive topic chains."""
    by_id={r['id']:r for r in rows};ts={i:tokens(r) for i,r in by_id.items()}
    freq=Counter(t for terms in ts.values() for t in terms)
    weights={t:math.log(1+len(rows)/(1+n)) for t,n in freq.items()}
    groups=[];assigned=set();index=defaultdict(set)
    # Retain explicit, existing multi-source comparison groups and identical headlines.
    for event in legacy:
        ids=[i for i in event.get('article_ids',[]) if i in by_id and i not in assigned]
        if not ids:continue
        if len(ids)>1 and any(by_id[i].get('research_status')=='preprint' for i in ids) and (not identity(by_id[ids[0]]) or any(identity(by_id[i])!=identity(by_id[ids[0]]) for i in ids)):
            groups.extend({'ids':[i],'basis':'single_report'} for i in ids);assigned.update(ids);continue
        groups.append({'ids':ids,'basis':event.get('grouping_basis','source_comparison') if len(ids)>1 else 'single_report','comparison':event.get('comparison')})
        assigned.update(ids)
    groups.extend({'ids':[r['id']],'basis':'single_report'} for r in rows if r['id'] not in assigned)
    # Deterministic oldest-first order makes the first anchor stable as news is added.
    groups.sort(key=lambda g:(min(by_id[i].get('published_at') or '' for i in g['ids']),min(g['ids'])))
    merged=[]
    for group in groups:
        anchor=by_id[group['ids'][0]];terms=ts[anchor['id']]
        counts=Counter(n for t in terms for n in index[t])
        candidates={n for n,count in counts.items() if count>=4}
        for t in terms:
            if t.startswith('@'):candidates.update(index[t])
        choices=[]
        for n in candidates:
            target=merged[n]
            anchors=target['ids'][:3]
            score=min(similarity(anchor,by_id[i],terms,ts[i],weights) for i in anchors)
            if score>=.56:choices.append((score,n))
        if choices:
            _,n=max(choices);merged[n]['ids'].extend(group['ids']);merged[n]['basis']='shared_event_evidence'
        else:
            n=len(merged);merged.append(group)
        for i in group['ids']:
            for t in ts[i]:index[t].add(n)
    return merged

def snapshot(row,day):
    keys=('id','title','title_zh','title_en','summary_zh','feed_excerpt','url','source_id','source_name','published_at','category','tags','content_type','geography','event_assignment')
    result={k:row[k] for k in keys if k in row}
    result['edition_date']=day
    return result

def published_editions(root):
    data=Path(root)/'data'; editions={}
    for p in sorted((data/'editions').glob('????-??-??.json')):
        revisions=list((data/'revisions'/p.stem).glob('[0-9]*.json'))
        source=max(revisions,key=lambda x:int(x.stem)) if revisions else p
        editions[p.stem]=json.loads(source.read_text(encoding='utf-8'))
    latest=data/'latest.json'
    if latest.exists():
        value=json.loads(latest.read_text(encoding='utf-8'))
        if value.get('date'):editions[value['date']]=value
    return [editions[k] for k in sorted(editions)]

def build_event_views(root=None, editions=None):
    from scripts.editorial import events as legacy_events
    from scripts.geography import country_mark, COUNTRIES
    editions=editions if editions is not None else published_editions(root)
    tracks={};days={};recent_index=defaultdict(set);article_track={};relations={}
    for edition in editions:
        day=edition['date'];rows=[r for r in edition.get('articles',[]) if r.get('section')!='背景阅读']
        by_id={r['id']:r for r in rows}
        if not rows:continue
        legacy=edition.get('events') or legacy_events(rows,edition.get('comparisons',[]))
        groups=group_day(rows,legacy);daily={}
        for group in groups:
            members=[by_id[i] for i in group['ids']]
            anchor=min(members,key=lambda r:(r.get('published_at') or '',r['id']))
            terms=tokens(anchor)
            known={article_track[r['id']] for r in members if r['id'] in article_track}
            counts=Counter(n for t in terms for n in recent_index[t])
            candidates={n for n,count in counts.items() if count>=4}
            for t in terms:
                if t.startswith('@'):candidates.update(recent_index[t])
            choices=[]
            for tid in candidates|known:
                track=tracks[tid]
                if day_distance(day,track['last_seen'])>14:continue
                previous=track['_anchor'];old=tokens(previous)
                # Cross-day continuity uses a stricter threshold than same-day grouping.
                score=similarity(anchor,previous,terms,old,{t:2 for t in terms|old})
                if tid in known:score=1
                if score>=.66:choices.append((score,tid))
            tid=max(choices)[1] if choices else 'story-'+hashlib.sha256(anchor['id'].encode()).hexdigest()[:16]
            if tid not in tracks:
                tracks[tid]={'id':tid,'title':event_title(anchor),'first_seen':day,'last_seen':day,'timeline':[],'relations':[],'_anchor':anchor,'_ids':set()}
            track=tracks[tid];track['last_seen']=day
            new=[r for r in members if r['id'] not in track['_ids']]
            if new:
                entry=next((p for p in track['timeline'] if p['date']==day),None)
                if entry is None:entry={'date':day,'reports':[]};track['timeline'].append(entry)
                entry['reports'].extend(snapshot(r,day) for r in sorted(new,key=lambda r:r.get('published_at') or '',reverse=True))
                track['_ids'].update(r['id'] for r in new)
            for r in members:article_track[r['id']]=tid
            for t in terms:recent_index[t].add(tid)
            if tid in daily:daily[tid]['article_ids'].extend(group['ids'])
            else:daily[tid]={'id':'event-'+tid,'story_id':tid,'article_ids':list(group['ids']),'grouping_basis':group['basis']}
            if group.get('comparison'):daily[tid]['comparison']=group['comparison']
        result=[]
        for tid,event in daily.items():
            event['article_ids']=list(dict.fromkeys(event['article_ids']))
            members=[by_id[i] for i in event['article_ids']]
            lead=max(members,key=lambda r:(r.get('published_at') or '',r['id']))
            track=tracks[tid]
            codes=list(dict.fromkeys(c for r in members for c in r.get('geography',{}).get('countries',[]) if c in COUNTRIES))[:8]
            event.update(lead_id=lead['id'],title=event_title(lead),category=lead['category'],categories=sorted({r['category'] for r in members}),first_seen=track['first_seen'],last_seen=day,
                         reporting_days=len({p['date'] for p in track['timeline']}),total_reports=len(track['_ids']),source_count=len({r['source_id'] for r in members}),
                         geography=country_mark(codes,'事件内来源报道提及') if codes else lead.get('geography'))
            result.append(event)
        result.sort(key=lambda e:by_id[e['lead_id']].get('published_at') or '',reverse=True)
        # Only explicit reported connections between separate country event clusters.
        active=[e for e in result if primary_countries(by_id[e['lead_id']]) and action(by_id[e['lead_id']])]
        for event in active:
            lead=by_id[event['lead_id']];ca=primary_countries(lead)
            for rid in event['article_ids']:
                r=by_id[rid];body=r.get('summary_zh') or r.get('feed_excerpt') or ''
                if not CONNECT.search(body):continue
                for other in active:
                    if other['story_id']==event['story_id']:continue
                    ob=by_id[other['lead_id']];cb=primary_countries(ob)
                    if ca&cb or not action(lead)&action(ob):continue
                    labels_a=[COUNTRIES[c][0] for c in ca if c in COUNTRIES];labels_b=[COUNTRIES[c][0] for c in cb if c in COUNTRIES]
                    sentences=re.split(r'(?<=[。！？])|(?<=\.)\s+',body)
                    evidence=next((s for s in sentences if CONNECT.search(s) and any(x in s for x in labels_a) and any(x in s for x in labels_b)),None)
                    if not evidence:continue
                    pair=tuple(sorted((event['story_id'],other['story_id'])))
                    # This is an attributed lead, never an assertion of verified causality.
                    relations[pair]={'type':'reported_connection','date':day,'evidence':evidence,'source_id':r['source_id'],'source_name':r.get('source_name') or r['source_id'],'url':r['url'],'article_id':rid}
        event_for={i:e for e in result for i in e['article_ids']};briefing=[];seen=set()
        for b in edition.get('briefing',[]):
            e=event_for.get(b.get('article_id'))
            if e and e['id'] not in seen:
                briefing.append(dict(b,event_id=e['id'],article_id=e['lead_id'],title=e['title'],summary=by_id[e['lead_id']].get('summary_zh') or b.get('summary','')));seen.add(e['id'])
        days[day]={'date':day,'revision':edition.get('revision',1),'event_version':2,'events':result,'briefing':briefing}
    for (a,b),evidence in relations.items():
        tracks[a]['relations'].append(dict(evidence,target=b,title=tracks[b]['title']))
        tracks[b]['relations'].append(dict(evidence,target=a,title=tracks[a]['title']))
    for day,view in days.items():
        for event in view['events']:
            event['relation_count']=sum(r['date']<=day for r in tracks[event['story_id']]['relations'])
    for track in tracks.values():
        track['timeline'].sort(key=lambda p:p['date'],reverse=True)
        for entry in track['timeline']:entry['reports'].sort(key=lambda r:r.get('published_at') or '',reverse=True)
        track['report_count']=len(track.pop('_ids'));track.pop('_anchor')
    return days,tracks

if __name__=='__main__':
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    days,tracks=build_event_views(Path(__file__).resolve().parents[1])
    last=days[max(days)]
    print(json.dumps({'date':last['date'],'events':len(last['events']),'reports':sum(len(e['article_ids']) for e in last['events']),'continuing':sum(e['reporting_days']>1 for e in last['events']),'dossiers':len(tracks)},ensure_ascii=False))
