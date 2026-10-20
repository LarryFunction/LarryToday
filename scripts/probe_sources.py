"""Read-only endpoint checks, isolated from production pools and editions."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

from scripts.update_news import ROOT, atomic_json, parse_feed
from scripts.collect import error_details


def probe(feed):
    result = dict(id=feed['id'], url=feed['url'], checked_at=datetime.now(timezone.utc).isoformat())
    try:
        if feed.get('adapter')=='xinhua_page':
            from scripts.news_pages import collect_page
            rows,errors=collect_page(feed)
            result.update(state='partial' if errors else 'parsed',count=len(rows),precise_count=len(rows),latest=max(r['published_at'] for r in rows),samples=rows[:2],article_errors=errors)
            return result
        request = urllib.request.Request(feed['url'], headers={'User-Agent': 'LarryToday/2.0 (source audit)'})
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read(2_000_001)
            result.update(http_status=response.status, final_url=response.url)
        if len(payload) > 2_000_000:
            raise ValueError('Response exceeds size limit')
        rows = parse_feed(payload, feed.get('source_id', feed['id']), feed.get('category', '科技与 AI'),limit=feed.get('max_items',24))
        result.update(state='parsed' if rows else 'empty', count=len(rows),
                      precise_count=sum(bool(r.get('published_at')) for r in rows),
                      latest=max((r.get('published_at') or r.get('published_day', '') for r in rows), default=None),
                      samples=rows[:2])
    except Exception as error:
        result.update(state='failed', **error_details(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config/feeds.json')
    parser.add_argument('--output', default='docs/source-probes.json')
    args = parser.parse_args()
    feeds = json.loads((ROOT / args.config).read_text(encoding='utf-8-sig'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, feeds))
    atomic_json(ROOT / args.output, results)
    print(json.dumps([{k:v for k,v in r.items() if k!='samples'} for r in results], ensure_ascii=True))


if __name__ == '__main__':
    main()
