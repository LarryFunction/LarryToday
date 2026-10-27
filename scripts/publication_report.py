"""Operator reports: aggregate metrics only, never secrets or raw exceptions."""
import json
import os
from datetime import datetime, timezone

def write_report(data, report):
    from scripts.update_news import atomic_json
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    atomic_json(data/'update-report.json',report)
    lines=['# LarryToday 出版报告','',f"状态：{report['state']}",f"目标刊期：{report.get('target_date','—')}",f"当前可读刊期：{report.get('published_date') or '—'}",'']
    for key,label in [('failed_sources','不可用订阅数'),('collected','抓取篇数'),('published','收录篇数'),('events','事件数'),('merged','合并减少的重复条目'),('sources','实际来源数'),('cached','AI 缓存命中'),('enriched','AI 新处理'),('failed','AI 处理失败'),('remaining','未完成 AI 编辑'),('prompt_tokens','输入 token'),('completion_tokens','输出 token'),('missing_usage','未返回用量的请求'),('accounted_tokens','预算核算用量'),('token_budget','预算上限'),('country_identified','具有国别标识'),('ai_country_decisions','AI 国别判断覆盖篇数')]:
        lines.append(f"- {label}：{report.get(key) if report.get(key) is not None else '未提供'}")
    lines+=['',f"处理阶段：{report.get('stage','完成')}",f"失败类型：{report.get('error_type') or '无'}",'用量为供应商返回数据；缺失值不视为零，预算核算并非账单。']
    lines+=['', '各 AI 阶段用量：', '```json', json.dumps(report.get('ai_stages',{}),ensure_ascii=False,indent=2), '```']
    text='\n'.join(lines)+'\n'
    (data/'update-report.md').write_text(text,encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:f.write(text)

def publication_report(edition, collected):
    rows=edition['articles']; ai=edition.get('ai_status',{}); usage=ai.get('usage',{})
    events=edition.get('events',[]); main=[r for r in rows if r.get('section')=='本期新闻']
    failures=sum(not s.get('ok',False) for s in edition.get('sources_status',[]))
    return {'failed_sources':failures,'ai_stages':usage.get('stages',{}),'budget_exhausted':ai.get('budget_exhausted',False),'state':'degraded' if failures or ai.get('state') in ('partial','unavailable','not_configured') else 'published',
        'target_date':edition['date'],'published_date':edition['date'],'collected':collected,'published':len(rows),
        'events':len(events),'merged':len(main)-len(events),'sources':len({r['source_id'] for r in main}),
        'country_identified':sum(bool(r.get('geography',{}).get('countries')) for r in rows),
        'ai_country_decisions':sum('country_mentions' in r for r in rows),
        **{k:ai.get(k) for k in ('cached','enriched','failed','remaining','accounted_tokens','token_budget')},
        **{k:usage.get(k) for k in ('prompt_tokens','completion_tokens','missing_usage')}}
