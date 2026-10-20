"""仅整理本地信源资料；不抓新闻、不开发网站。Python 3.10+，仅标准库。"""
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from collections import Counter, defaultdict
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-18'
KINDS = {'news': '新闻报道', 'official': '机构一手材料', 'data': '数据',
         'research': '研究', 'company': '企业自述', 'analysis': '分析评论',
         'factcheck': '事实核查', 'discovery': '发现线索'}
ROLES = {'news': 'reporting', 'official': 'primary_statement_or_record',
         'data': 'dataset', 'research': 'research_evidence', 'company': 'interested_party_statement',
         'analysis': 'interpretation', 'factcheck': 'verification_analysis', 'discovery': 'lead_only'}

def dump(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def normalize(url):
    p = urlsplit(url if '://' in url else 'https://' + url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', p.query, ''))

def host(url):
    return (urlsplit(url).hostname or '').lower().removeprefix('www.')

def write_csv(name, rows, fields):
    with (ROOT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            out = {}
            for k in fields:
                v = row.get(k)
                if isinstance(v, (list, dict)):
                    v = json.dumps(v, ensure_ascii=False)
                if isinstance(v, str) and v.startswith(('=', '+', '-', '@')):
                    v = "'" + v  # 避免用表格软件打开CSV时当作公式
                out[k] = v
            w.writerow(out)

def main():
    original = {}
    legacy = {}
    notes = []
    text_by_file = {}
    pattern = re.compile(r'(?:https?://|www\.)[A-Za-z0-9._~:/?#\[\]@!$&\x27()*+,;=%-]+')
    for path in sorted((ROOT / 'examples').glob('*.txt')):
        raw = path.read_bytes()
        original[path.name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        text = raw.decode('utf-8-sig')
        text_by_file[path.name] = text
        for number, line in enumerate(text.splitlines(), 1):
            found = list(pattern.finditer(line))
            if not found and line.strip():
                notes.append({'file': 'examples/' + path.name, 'line': number, 'text': line.strip(),
                              'status': 'legacy_unreviewed_note'})
            for m in found:
                raw_url = m.group().rstrip('.,;:!?)')
                url = normalize(raw_url)
                if not urlsplit(url).hostname or '.' not in urlsplit(url).hostname:
                    continue
                key = url
                item = legacy.setdefault(key, {'url': url, 'host': host(url), 'references': [],
                                               'status': 'legacy_unverified',
                                               'note': '仅提取原文URL；不继承可访问性、权威性、国别或立场判断'})
                item['references'].append({'file': 'examples/' + path.name, 'line': number, 'raw_url': raw_url})
    legacy_list = sorted(legacy.values(), key=lambda x: x['url'])
    by_host = defaultdict(list)
    for item in legacy_list:
        by_host[item['host']].extend(item['references'])
    dump('legacy-url-index.json', legacy_list)
    dump('legacy-unresolved-notes.json', notes)
    write_csv('legacy-url-index.csv', legacy_list, ['url', 'host', 'status', 'references'])

    checks = json.loads((ROOT / 'verification-log.json').read_text(encoding='utf-8'))
    checks_by_url = {x['url']: x for x in checks}
    aliases = {'arxiv': ['arXiv.org'], 'openalex': ['OpenAlex'], 'pubmed': ['PubMed'],
               'biorxiv': ['bioRxiv'], 'medrxiv': ['medRxiv'], 'repec': ['RePEc'],
               'reddit': ['Reddit'], 'v2ex': ['V2EX'], 'neurips': ['NeurIPS']}
    families = {'reuters': 'reuters', 'reuterscheck': 'reuters', 'ap': 'ap', 'apcheck': 'ap',
                'afp': 'afp', 'afpcheck': 'afp', 'guardian': 'guardian', 'guardian-api': 'guardian',
                'nyt': 'nyt', 'nyt-api': 'nyt', 'deepmind': 'google', 'google-research': 'google',
                'googlezero': 'google', 'google-news': 'google', 'fed': 'federal-reserve-system',
                'fred': 'federal-reserve-system', 'alfred': 'federal-reserve-system'}
    priority = set('reuters ap afp bbc guardian aljazeera nhk cna xinhua caixin yicai restworld rnz continent publica arxiv openreview deepseek qwen hf anthropic deepmind stanfordhai epoch artificialanalysis ft bloomberg worldbank imf fed ecb pbc bls stats-cn sec cninfo hkex unnews undocs reliefweb who pubmed usgs carbonbrief mongabay afpcheck icij oc crp'.split())
    priority.discard('oc'); priority.discard('crp'); priority.add('occrp')
    catalog = []
    categories = {}
    category = None
    for number, line in enumerate((ROOT / 'catalog.seed.psv').read_text(encoding='utf-8').splitlines(), 1):
        if line.startswith('## '):
            category, label = line[3:].split(' ', 1)
            categories[category] = label
        elif line and not line.startswith('#'):
            parts = line.split('|')
            assert len(parts) == 7, (number, parts)
            sid, name, url, region, langs, kind, note = parts
            assert category and kind in KINDS
            matches = by_host.get(host(url), [])
            name_matches = []
            for filename, text in text_by_file.items():
                for alias in aliases.get(sid, []):
                    for ln, content in enumerate(text.splitlines(), 1):
                        if alias.casefold() in content.casefold():
                            name_matches.append({'file': 'examples/' + filename, 'line': ln, 'matched_name': alias})
            check = checks_by_url.get(url)
            catalog.append({'id': sid, 'name': name, 'url': url, 'category': category,
                'coverage_regions': region.split(','), 'languages': langs.split(','), 'kind': kind,
                'evidence_role': ROLES[kind], 'usage_notes': note,
                'priority': 'P1' if sid in priority else ('P3' if kind == 'discovery' else 'P2'),
                'publisher_family_hint': families.get(sid),
                'ownership_verified': False,
                'relationship_to_examples': 'existing_host_enriched' if matches else ('existing_name_enriched' if name_matches else 'supplemental_candidate'),
                'example_references': matches + name_matches,
                'verification_status': check['status'] if check else 'not_checked',
                'checked_at': check['checked_at'] if check else None,
                'evidence_url': url if check else None,
                'observed_title': check.get('title') if check else None,
                'observed_redirect': check.get('redirect') if check else None,
                'access_and_reuse': 'unknown_per_item_check_required',
                'enabled_for_ingestion': False, 'integration_ids': []})
    ids = {r['id'] for r in catalog}
    assert len(ids) == len(catalog), 'duplicate source id'
    assert len({normalize(r['url']) for r in catalog}) == len(catalog), 'duplicate source URL'
    integrations = []
    for line in (ROOT / 'integrations.seed.psv').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        sid, mode, doc, endpoint, auth, note = line.split('|')
        assert sid in ids
        integrations.append({'id': sid + '-' + mode, 'source_id': sid, 'method': mode,
            'documentation_url': doc, 'endpoint_url': endpoint or None, 'auth_notes': auth,
            'notes': note, 'documentation_status': checks_by_url.get(doc, {}).get('status', 'not_checked'),
            'endpoint_status': 'not_integration_tested', 'enabled': False})
    probes_path = ROOT / 'endpoint-probes.json'
    probes = {r['integration_id']: r for r in json.loads(probes_path.read_text(encoding='utf-8'))} if probes_path.exists() else {}
    for item in integrations:
        if item['id'] in probes:
            item['endpoint_status'] = probes[item['id']]['status']
            item['endpoint_checked_at'] = probes[item['id']]['checked_at']
    for r in catalog:
        r['integration_ids'] = [i['id'] for i in integrations if i['source_id'] == r['id']]
    assert len({i['id'] for i in integrations}) == len(integrations)
    for r in catalog:
        assert urlsplit(r['url']).scheme in ('http', 'https') and urlsplit(r['url']).netloc
    dump('sources.json', {'schema_version': '1.0', 'prepared_at': DATE, 'categories': categories, 'sources': catalog})
    dump('integrations.json', integrations)
    write_csv('sources.csv', catalog, ['id', 'name', 'url', 'category', 'coverage_regions', 'languages', 'kind',
        'priority', 'evidence_role', 'usage_notes', 'publisher_family_hint', 'relationship_to_examples',
        'verification_status', 'checked_at', 'observed_redirect', 'integration_ids', 'example_references'])
    write_csv('integrations.csv', integrations, list(dict.fromkeys(k for r in integrations for k in r)))
    md = ['# LarryToday 扩充信源目录', '', f'整理日期：{DATE}。共 {len(catalog)} 条；包含原有来源的补全，不等于全部新增。', '',
          '网页核验只表示研究工具读到了页面，不保证实时连通、持续更新、编辑质量或采集许可。',
          '所有条目默认禁用自动采集；本轮不开发网站。P1/P2/P3是接入研究优先级，不是真实性评分。', '',
          '字段、核验状态及文件说明见 [README](README.md) 与 [字段说明](SCHEMA.md)。', '']
    for cat, label in categories.items():
        rows = [r for r in catalog if r['category'] == cat]
        md.extend([f'## {label}（{len(rows)}）', '', '| ID / 来源 | 区域 / 语言 | 类型 / 优先级 | 用途与局限 | 页面核验 |', '|---|---|---|---|---|'])
        for r in rows:
            state = {'page_observed': '已读到页面', 'fetch_inconclusive': '待复核', 'not_checked': '未检查'}[r['verification_status']]
            md.append(f"| `{r['id']}` [{r['name']}]({r['url']}) | {', '.join(r['coverage_regions'])} / {', '.join(r['languages'])} | {KINDS[r['kind']]} / {r['priority']} | {r['usage_notes']} | {state} |")
        md.append('')
    (ROOT / 'CATALOG.md').write_text('\n'.join(md), encoding='utf-8')
    unresolved = ['# 需要复核的入口', '', '失败不代表停运或用户无法访问；本次未使用用户VPN。重定向保留原入口，接入时确认栏目及身份。', '']
    for r in catalog:
        if r['verification_status'] != 'page_observed' or r['observed_redirect']:
            unresolved.append(f"- `{r['id']}` [{r['name']}]({r['url']})：{r['verification_status']}" + (f"；观察到跳转：{r['observed_redirect']}" if r['observed_redirect'] else ''))
    (ROOT / 'LINK_REVIEW.md').write_text('\n'.join(unresolved) + '\n', encoding='utf-8')
    stats = {'prepared_at': DATE, 'curated_sources': len(catalog), 'categories': dict(Counter(r['category'] for r in catalog)),
             'kinds': dict(Counter(r['kind'] for r in catalog)), 'verification': dict(Counter(r['verification_status'] for r in catalog)),
             'relationship_to_examples': dict(Counter(r['relationship_to_examples'] for r in catalog)),
             'legacy_unique_urls': len(legacy_list), 'legacy_url_occurrences': sum(len(r['references']) for r in legacy_list),
             'legacy_non_url_lines': len(notes), 'integration_entries': len(integrations),
             'unique_hosts_union': len({host(r['url']) for r in catalog + legacy_list}),
             'example_files': original}
    dump('manifest.json', stats)
    print(json.dumps({k: v for k, v in stats.items() if k != 'example_files'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
