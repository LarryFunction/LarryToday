"""离线检查资料引用、URL、数量、原文件哈希与OPML；不请求网络。"""
from pathlib import Path
from urllib.parse import urlsplit
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

def main():
    data, manifest = read('sources.json'), read('manifest.json')
    sources = data['sources']
    ids = {x['id'] for x in sources}
    assert len(ids) == len(sources) == manifest['curated_sources']
    assert len({x['url'] for x in sources}) == len(sources)
    required = set(read('sources.schema.json')['properties']['sources']['items']['required'])
    integrations = read('integrations.json')
    integration_ids = {x['id'] for x in integrations}
    assert len(integration_ids) == len(integrations) == manifest['integration_entries']
    checks = {x['url']: x for x in read('verification-log.json')}
    for s in sources:
        assert set(s) == required, s['id']
        assert s['category'] in data['categories']
        assert s['enabled_for_ingestion'] is False
        assert s['ownership_verified'] is False
        assert set(s['integration_ids']) <= integration_ids
        assert s['url'] in checks, s['id']
        assert s['verification_status'] == checks[s['url']]['status'], s['id']
        assert s['checked_at'] == checks[s['url']]['checked_at']
        for ref in s['example_references']:
            lines = (ROOT / ref['file']).read_text(encoding='utf-8-sig').splitlines()
            needle = ref.get('raw_url', ref.get('matched_name'))
            assert needle.casefold() in lines[ref['line'] - 1].casefold(), ref
    for integration in integrations:
        assert integration['source_id'] in ids
        assert integration['enabled'] is False
    for recipe in read('verification-recipes.json'):
        for key in ['primary_candidates', 'reporting_candidates', 'regional_candidates', 'verification_candidates']:
            assert set(recipe[key]) <= ids, (recipe['id'], key, set(recipe[key]) - ids)
    legacy = read('legacy-url-index.json')
    assert len(legacy) == manifest['legacy_unique_urls']
    for record in sources + legacy:
        u = urlsplit(record['url'])
        assert u.scheme in ('http', 'https') and u.hostname and '.' in u.hostname, record['url']
    for record in legacy:
        for ref in record['references']:
            line = (ROOT / ref['file']).read_text(encoding='utf-8-sig').splitlines()[ref['line'] - 1]
            assert ref['raw_url'] in line
    for name, meta in manifest['example_files'].items():
        raw = (ROOT / 'examples' / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == meta['sha256']
        assert len(raw) == meta['bytes']
    for name, count in [('sources.csv', len(sources)), ('integrations.csv', len(integrations)), ('legacy-url-index.csv', len(legacy))]:
        with (ROOT / name).open(encoding='utf-8-sig', newline='') as f:
            assert len(list(csv.DictReader(f))) == count
    probes = read('endpoint-probes.json')
    checked_feeds = {x['url'] for x in probes if x['status'] == 'feed_parsed'}
    opml = ET.parse(ROOT / 'feeds.checked.opml')
    assert {x.attrib['xmlUrl'] for x in opml.findall('.//outline')} == checked_feeds
    for probe in probes:
        integration = next(x for x in integrations if x['id'] == probe['integration_id'])
        assert integration['endpoint_status'] == probe['status']
    print(f'PASS: {len(sources)} sources, {len(legacy)} legacy URLs, {len(integrations)} integrations, '
          f'{len(read("verification-recipes.json"))} recipes, {len(checked_feeds)} OPML feeds; references and original file hashes consistent.')

if __name__ == '__main__':
    main()
