"""Shared read-only payload builders for the HTTP server and static Pages export."""
import json
from pathlib import Path


def merged_sources(root):
    root = Path(root)
    catalog = json.loads((root / 'srcs' / 'sources.json').read_text(encoding='utf-8'))
    existing = {source['id'] for source in catalog['sources']}
    for feed in json.loads((root / 'config' / 'feeds.json').read_text(encoding='utf-8')):
        if feed['source_id'] in existing:
            continue
        catalog['sources'].append({
            'id': feed['source_id'],
            'name': feed['name'],
            'url': feed['url'],
            'category': feed['category'],
            'languages': [],
            'coverage_regions': [feed['region']],
            'usage_notes': '已配置订阅；实际可用性见接入状态。',
        })
        existing.add(feed['source_id'])
    return catalog
