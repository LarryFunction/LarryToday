"""Build the static GitHub Pages site from public assets and published data."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.site_payloads import merged_sources


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copy_json(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def build_site(root=ROOT, out=None):
    root = Path(root)
    out = Path(out) if out is not None else root / 'dist'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for asset in ('index.html', 'style.css', 'app.js'):
        shutil.copy2(root / 'public' / asset, out / asset)
    (out / '.nojekyll').write_text('', encoding='utf-8')

    api = out / 'api'
    api.mkdir()
    for source, target in (
        ('latest.json', 'news.json'),
        ('archive.json', 'archive.json'),
        ('last-update.json', 'status.json'),
        ('source-health.json', 'source-health.json'),
        ('social-status.json', 'social-status.json'),
        ('social-posts.json', 'social-posts.json'),
    ):
        path = root / 'data' / source
        if path.exists():
            shutil.copy2(path, api / target)

    catalog = merged_sources(root)
    write_json(api / 'sources.json', catalog)

    latest_path = root / 'data' / 'latest.json'
    latest = read_json(latest_path) if latest_path.exists() else {}
    latest_date = latest.get('date')

    edition_days = []
    editions = root / 'data' / 'editions'
    if editions.exists():
        (api / 'editions').mkdir(parents=True, exist_ok=True)
        for path in sorted(editions.glob('*.json')):
            shutil.copy2(path, api / 'editions' / path.name)
            edition_days.append(path.stem)
    if latest_date and latest_date not in edition_days:
        write_json(api / 'editions' / f'{latest_date}.json', latest)
        edition_days.append(latest_date)

    revisions = root / 'data' / 'revisions'
    if revisions.exists():
        for day_dir in sorted(path for path in revisions.iterdir() if path.is_dir()):
            index = day_dir / 'index.json'
            if index.exists():
                copy_json(index, api / 'revisions' / f'{day_dir.name}.json')
            for path in sorted(day_dir.glob('*.json')):
                if path.name != 'index.json':
                    copy_json(path, api / 'revisions' / day_dir.name / path.name)

    archive = read_json(api / 'archive.json') if (api / 'archive.json').exists() else []
    archive = sorted({day for day in archive if day in edition_days}, reverse=True)
    if latest_date and latest_date not in archive:
        archive.insert(0, latest_date)
    write_json(api / 'archive.json', archive)

    for day in archive:
        if not (api / 'revisions' / f'{day}.json').exists():
            edition = read_json(api / 'editions' / f'{day}.json')
            write_json(api / 'revisions' / f'{day}.json', [{
                'revision': 1,
                'note': '初版（旧格式）',
                'published_at': edition.get('updated_at') or edition.get('date'),
            }])

    return {
        'output': str(out),
        'editions': len(edition_days),
        'archived_editions': len(archive),
        'sources': len(catalog['sources']),
        'articles': len(latest.get('articles', [])),
    }


if __name__ == '__main__':
    print(json.dumps(build_site(), ensure_ascii=False))
