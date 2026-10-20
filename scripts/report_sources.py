"""Build a credential-free, reproducible source maintenance report."""
import json
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def cell(value): return str('—' if value is None or value=='' else value).replace('|',' / ').replace('\n',' ')
def local(value):
    if not value: return '—'
    return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
def report():
    catalog=read('srcs/sources.json');feeds=read('config/feeds.json');health=read('data/source-health.json')
    social=read('config/social.json');edition=read('data/latest.json')
    connected={f['source_id'] for f in feeds};unconnected=[s for s in catalog['sources'] if s['id'] not in connected]
    states=Counter(h['state'] for h in health)
    names={'available':'可用且含精确时间','empty':'有效空订阅','stale':'订阅过时','date_only':'缺少精确时间','unavailable':'请求或解析失败','disabled':'未启用','partial':'部分文章成功'}
    lines=['# LarryToday 信息源排查与接入维护文档','',f"报告生成：{local(datetime.now(timezone.utc).isoformat())}（北京时间）",f"最近采集：{local(max(h['checked_at'] for h in health))}（北京时间）",'',
    '## 先看结论','',
    f"- 原始目录 {len(catalog['sources'])} 家；配置 {len(feeds)} 个入口，对应 {len(connected)} 个来源ID。一个媒体可有多个栏目入口。",
    f"- 原始目录中尚无采集配置：{len(unconnected)} 家。它们是“尚未接入/未验证”，不能直接判为无法连接。",
    '- 本轮状态：'+ '；'.join(f'{names.get(k,k)} {v} 个' for k,v in states.items())+'。',
    f"- 当前已发布刊期 {edition['date']}，修订 {edition.get('revision',1)}。本报告复测发生在截稿后，采集池新增内容不会自动改写本期。",
    '- 目录中某媒体存在、订阅返回成功、文章被收入本期，是三个不同阶段；“未收录”不一定是故障。','',
    '## 维护说明','',
    '本文件按最新采集结果生成。修复内容、证据、未解决项和手动操作方案见 [信息源处理报告](source-treatment-report.md)。',
    '空订阅、停更、日期不完整、请求失败分别记录；页面适配器可能只有部分文章成功。配置数量不代表完整覆盖。',
    'arXiv RSS 使用公告时间，修订与新稿分别标记；Nature 的日期级元数据留在背景候选池，不进入精确截稿窗口。','',
    f'## 当前{len(feeds)}个入口实测明细','',
    '这是一份时间点快照。网络、服务器所在地与订阅更新都会影响后续结果。HTTP错误和连接异常仅记录类型，不包含凭证。','',
    '| 来源 / 入口ID | 状态 | 条目数 | 最新稿日期 | HTTP / 错误类型 | 最近成功（北京时间） | 已配置入口 |',
    '|---|---|---:|---|---|---|---|']
    for h in health:
        lines.append('| '+' | '.join(cell(x) for x in [h['name']+' / '+h['id'],names.get(h['state'],h['state']),h.get('count',0),h.get('latest_article') or h.get('latest_day'),h.get('http_status') or h.get('error'),local(h.get('last_success')),h['url']])+' |')
    lines+=['','## 处理方法','',
    '1. **404**：先核对官方当前地址及重定向；找到候选地址后实际解析，不能仅凭搜索结果改配置。',
    '2. **连接失败**：区分DNS、TLS、超时和服务器地区问题。查看健康记录 error_kind（dns/tls/timeout/http/connection/parse_or_validation），并在目标云服务器复测；不关闭TLS验证。',
    '3. **停更**：检查订阅最新稿日期，与官网近期稿件比对。入口返回200不等于内容新鲜。',
    '4. **没有RSS**：可开发针对公开栏目页的适配器；提取真实标题、日期、短摘要与原文URL，逐站检查使用条件。网站结构变动后需要维护。',
    '5. **需要授权**：使用官方授权接口或人工导入；是否需要付费必须逐站核实。本报告未断言所有未接入媒体都需要付费。',
    '6. **个人观点**：可补接作者公开博客或Newsletter的RSS，作为单独观点来源；不能声称覆盖其全部X发言。',
    '7. **收录为空**：先查采集池，再查发布时间/截稿窗口/去重/消费推荐过滤。新闻不在本期不一定是采集失败。','',
    '## 文件和复测命令','',
    '| 文件 | 用途 |','|---|---|',
    '| `config/feeds.json` | RSS入口、来源ID、主题、地区、机构归属、启用开关 |',
    '| `srcs/sources.json` | 原始候选来源目录；这里列出并不会自动采集 |',
    '| `config/social.json` | X观察账号与启用开关 |',
    '| `scripts/collect.py` | 采集和健康状态判定 |',
    '| `scripts/update_news.py` | 解析、截稿、AI编辑与发布 |',
    '| `data/source-health.json` | 最近一轮逐入口结果 |',
    '| `data/article-pool.json` | 滚动素材池；不等于已发布日报 |',
    '| `data/social-status.json` | X配置及采集状态，不含凭证 |','',
    '```powershell',
    '# 只采集，不调用新闻编辑AI，不发布新刊',
    'python -m scripts.collect',
    '# 根据最新健康记录重新生成本文档',
    'python scripts/report_sources.py',
    '# 验证解析和日报逻辑',
    'python -m unittest discover -s tests','```','',
    '密钥只放服务器本地 `.env`，不要粘贴进本文档、截图或版本库。新增源先采集验证，再决定是否发布修订；不要把故障排查当成自动改写历史刊期。','',
    '## 待接入来源完整清单','',
    '以下按原始目录分类列出所有尚无feeds配置的来源。优先级与备注来自原目录，不代表本轮已逐一验证其接口、授权或可达性。没有配置的来源统一状态为“待发现入口、待验证”。','']
    for category,label in catalog['categories'].items():
        group=[s for s in unconnected if s['category']==category]
        if not group: continue
        lines += [f'### {label}（{len(group)}家）','', '| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |','|---|---|---|---|---|']
        for s in group:
            lines.append('| '+' | '.join(cell(x) for x in [s.get('priority'),s['name']+' / '+s['id'],'、'.join(s.get('coverage_regions',[])),s['url'],s.get('usage_notes')])+' |')
        lines.append('')
    lines+=['## X观察账号清单','', '身份状态逐账号记录；official_site_linked 表示作者官网有对应账号链接，不代表发言内容经过核实。其余账号仍待核验。','', '| 用户名 | 名称 | 身份状态 |','|---|---|---|']
    for a in social['accounts']: lines.append('| '+' | '.join(cell(a.get(k)) for k in ('username','name','identity_status'))+' |')
    output=ROOT/'docs/source-audit.md';output.parent.mkdir(exist_ok=True);output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(output),'configured_feeds':len(feeds),'configured_sources':len(connected),'unconfigured_catalog_sources':len(unconnected),'health':dict(states)},ensure_ascii=True))
if __name__=='__main__': report()
