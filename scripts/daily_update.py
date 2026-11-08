"""Idempotent scheduled publication. Credentials come only from environment."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.editorial import window
from scripts.update_news import publish, atomic_json, translation_gap


def ai_enabled(config):
    setting=config.get('AI_ENABLED','').strip().lower()
    if setting in ('false','0','off'): return False
    return setting == 'true' or all(config.get(k) for k in ('BASE_URL','BASE_KEY_1','BASE_KEY_2','BASE_KEY_3'))


def run():
    day = window()['date']
    data=ROOT/'data'
    latest=data/'latest.json'
    if latest.exists():
        edition=json.loads(latest.read_text(encoding='utf-8'))
        draft=data/'pending'/f"{edition['date']}.json"
        if translation_gap(edition.get('articles',[])) and not draft.exists():
            atomic_json(draft,edition)
    pending=sorted((data/'pending').glob('????-??-??.json'))
    if (data / 'editions' / f'{day}.json').exists() and not pending:
        from scripts.publication_report import write_report
        write_report(ROOT/'data',{'state':'skipped','target_date':day,'published_date':day})
        print(f'{day} already published; no paid calls or automatic revision.')
        return
    enabled = ai_enabled(os.environ)
    if enabled and not all(os.environ.get(k) for k in ('BASE_URL', 'BASE_KEY_1', 'BASE_KEY_2', 'BASE_KEY_3')):
        enabled=False
        print('::warning::AI secrets incomplete; retaining draft without paid calls')
    if not enabled:
        print('::warning::AI translation disabled: incomplete editions will remain drafts.')
    os.environ.setdefault('AI_DAILY_LEDGER',str(data/'ai-budget-ledger.json'))
    os.environ.setdefault('AI_TOKEN_BUDGET','500000')
    # Capture today's finite feed window before spending time on any backlog.
    if not (data/'editions'/f'{day}.json').exists() and not (data/'pending'/f'{day}.json').exists():
        publish(ai=False,edition_date=day,require_complete=True)
    pending=sorted((data/'pending').glob('????-??-??.json'))
    # Oldest drafts first; every retry shares the same daily ledger.
    days=list(dict.fromkeys([p.stem for p in pending]+[day]))
    for target in days:
        published=(data/'editions'/f'{target}.json').exists()
        if published and not (data/'pending'/f'{target}.json').exists():continue
        result=publish(ai=enabled,edition_date=target,require_complete=True,
                       revision_note='补全暂存日报译文' if published else None)
        print(json.dumps({'date':result['date'],'count':result['count'],'state':result.get('state','published')},ensure_ascii=False))


if __name__ == '__main__':
    run()
