"""Build the static GitHub Pages site from public assets and published data."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.site_payloads import merged_sources
from scripts.geography import geography


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copy_json(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    value=read_json(source)
    if isinstance(value,dict) and 'articles' in value:
        value['articles']=[dict(r,geography=geography(r)) for r in value['articles']]
    write_json(target,value)


def paged_payload(edition):
    """Keep full archives; latest reader downloads index and needed chunks."""
    chunks=[]
    articles=edition.get('articles',[])
    manifest={k:v for k,v in edition.items() if k!='articles'}
    # Reader grouping is a presentation view; archived editions stay unchanged.
    if edition.get('events') is not None:
        from scripts.editorial import events
        main=[r for r in articles if r.get('section')!='背景阅读']
        manifest['events']=events(main,edition.get('comparisons',[]))
        event_for={id:e['id'] for e in manifest['events'] for id in e['article_ids']}
        manifest['briefing']=[dict(b,event_id=event_for.get(b.get('article_id'),b.get('event_id'))) for b in edition.get('briefing',[])]
    manifest['paged']=True
    manifest['articles']=[]
    for offset in range(0,len(articles),30):
        chunk=f'api/chunks/{offset//30}.json'
        rows=[]
        for original in articles[offset:offset+30]:
            row=dict(original,geography=geography(original))
            rows.append(row)
            small={k:row[k] for k in ('id','title','title_zh','title_en','category','source_id','source_name','published_at','url','tags','section','geography') if k in row}
            small['_chunk']=chunk
            small['_search']=' '.join(str(row.get(k) or '') for k in ('summary_zh','summary'))
            manifest['articles'].append(small)
        chunks.append(rows)
    return manifest,chunks

def write_paged(api, edition):
    manifest,chunks=paged_payload(edition)
    for i,rows in enumerate(chunks): write_json(api/'chunks'/f'{i}.json',rows)
    write_json(api/'reader.json',manifest)


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
    write_paged(api, latest)

    edition_days = []
    editions = root / 'data' / 'editions'
    if editions.exists():
        (api / 'editions').mkdir(parents=True, exist_ok=True)
        for path in sorted(editions.glob('*.json')):
            copy_json(path, api / 'editions' / path.name)
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
        if not (api / 'revisions' / day / '1.json').exists():
            copy_json(api / 'editions' / f'{day}.json', api / 'revisions' / day / '1.json')
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
