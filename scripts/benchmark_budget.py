"""Small, bounded live benchmark for planning. Never changes the daily limit."""
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from scripts.ai_news import Client, settings, evidence, VERSION, translate_batch
from scripts.editorial import classify
from scripts.update_news import atomic_json

ROOT=Path(__file__).resolve().parents[1]

def run():
    config=settings();config['AI_TOKEN_BUDGET']='20000'
    client=Client(config);client.discover()
    latest=json.loads((ROOT/'data/latest.json').read_text(encoding='utf-8'))
    groups=defaultdict(list)
    for original in latest['articles']:
        row=classify(dict(original))
        if not row.get('title_zh') or not row.get('summary_zh'):groups[row['category']].append(row)
    sample=[]
    for category,rows in sorted(groups.items()):
        rows.sort(key=lambda r:len(r.get('feed_excerpt') or ''))
        for index in sorted({0,len(rows)//2,len(rows)-1}):sample.append(rows[index])
    batches=[]; sample=sample[:18]
    for offset in range(0,len(sample),6):
        batch=sample[offset:offset+6];before=dict(client.usage)
        result=translate_batch(client,batch)
        usage={k:client.usage[k]-before.get(k,0) for k in ('prompt_tokens','completion_tokens','reasoning_tokens','calls')}
        batches.append({'articles':len(batch),'valid':len(result),'categories':sorted({r['category'] for r in batch}),**usage})
        for row in batch:
            if row['id'] not in result:continue
            signature=hashlib.sha256(json.dumps([VERSION,client.model,evidence(row)],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            atomic_json(ROOT/'data/ai-cache'/('translation-v1-'+signature+'.json'),result[row['id']])
        print(json.dumps(batches[-1],ensure_ascii=True),flush=True)
    report={'date':latest['date'],'model':client.model,'thinking':'disabled','sample_size':len(sample),'batches':batches,'usage':client.usage,'accounted_tokens':client.used_bound,'sample_ids':[r['id'] for r in sample]}
    atomic_json(ROOT/'docs/budget-benchmark.json',report)
    return report

if __name__=='__main__':run()
