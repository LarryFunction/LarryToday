"""Idempotent scheduled publication. Credentials come only from environment."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.editorial import window
from scripts.update_news import publish


def run():
    day = window()['date']
    if (ROOT / 'data' / 'editions' / f'{day}.json').exists():
        from scripts.publication_report import write_report
        write_report(ROOT/'data',{'state':'skipped','target_date':day,'published_date':day})
        print(f'{day} already published; no paid calls or automatic revision.')
        return
    enabled = os.environ.get('AI_ENABLED', '').lower() == 'true'
    if enabled and not all(os.environ.get(k) for k in ('BASE_URL', 'BASE_KEY_1', 'BASE_KEY_2', 'BASE_KEY_3')):
        enabled=False
        print('::warning::AI secrets incomplete; publishing original news without paid calls')
    result = publish(ai=enabled, edition_date=day)
    print(json.dumps({'date': result['date'], 'count': result['count'], 'ai': result['ai']}, ensure_ascii=False))


if __name__ == '__main__':
    run()
