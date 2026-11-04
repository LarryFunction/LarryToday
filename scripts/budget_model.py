"""Offline budget planning; recommendations never mutate production limits."""
import json,math,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def estimate(new_articles, per_article=300):
    # 20% retry/length allowance; selection, detail editing, request reservation.
    return math.ceil((new_articles*per_article*1.2+12000+20000+20000)/10000)*10000

def run():
    benchmark=json.loads((ROOT/'docs/budget-benchmark.json').read_text(encoding='utf-8'))
    batches=benchmark['batches']
    worst=max((b['prompt_tokens']+b['completion_tokens'])/b['valid'] for b in batches if b['valid'])
    unit=math.ceil(worst*1.2/50)*50
    history=[]
    for p in sorted((ROOT/'data/editions').glob('*.json')):
        d=json.loads(p.read_text(encoding='utf-8'));rows=d['articles']
        if d['date']<'2026-10-23':continue
        foreign=sum(not (re.search('[\u4e00-\u9fff]',r.get('title') or '') and re.search('[\u4e00-\u9fff]',r.get('feed_excerpt') or '')) for r in rows)
        history.append({'date':d['date'],'articles':len(rows),'new_foreign_no_cache':foreign,'planned_tokens':estimate(foreign,unit)})
    recommendation=math.ceil(max(r['planned_tokens'] for r in history)/100000)*100000
    report={'sample_size':benchmark['sample_size'],'sample_tokens':sum(b['prompt_tokens']+b['completion_tokens'] for b in batches),'conservative_unit_tokens':unit,'retry_margin':.2,'fixed_reserve':52000,'history':history,'recommended_daily_cap':recommendation,'production_cap_changed':False,'assumptions':['Small stratified pilot; no statistical coverage guarantee','Assumes zero reusable cache and existing Chinese material needs no translation','Planning bound is not a currency bill','Detail editing and morning selection are capped; all original news retained']}
    (ROOT/'docs/budget-model.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))
    return report
if __name__=='__main__':run()
