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
        print(f'{day} already published; no paid calls or automatic revision.')
        return
    enabled = os.environ.get('AI_ENABLED', '').lower() == 'true'
    if enabled and not all(os.environ.get(k) for k in ('BASE_URL', 'BASE_KEY_1', 'BASE_KEY_2', 'BASE_KEY_3')):
        raise ValueError('AI enabled but required repository secrets are missing')
    result = publish(ai=enabled)
    print(json.dumps({'date': result['date'], 'count': result['count'], 'ai': result['ai']}, ensure_ascii=False))


if __name__ == '__main__':
    run()
