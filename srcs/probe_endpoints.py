"""低频只读检查少量公开RSS/JSON样本；不下载新闻正文、不绕过登录或付费墙。"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

def probe(item):
    result = {'integration_id': item['id'], 'url': item['endpoint_url'],
              'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'inconclusive'}
    try:
        request = Request(item['endpoint_url'], headers={'User-Agent': 'LarryToday-source-audit/0.1'})
        with urlopen(request, timeout=18) as response:
            result.update(http_status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type'))
            payload = response.read(4_000_001)
        if len(payload) > 4_000_000:
            raise ValueError('response exceeds 4 MB audit cap')
        if item['method'] == 'rss':
            root = ET.fromstring(payload)
            tag = root.tag.rsplit('}', 1)[-1]
            if tag not in ('rss', 'feed', 'RDF'):
                raise ValueError('not RSS/Atom/RDF')
            entries = root.findall('.//item') + root.findall('{http://www.w3.org/2005/Atom}entry')
            result.update(status='feed_parsed' if entries else 'empty_feed', format=tag, entries=len(entries))
        else:
            data = json.loads(payload)
            if not isinstance(data, dict) or data.get('type') != 'FeatureCollection' or not isinstance(data.get('features'), list):
                raise ValueError('unexpected GeoJSON shape')
            result.update(status='geojson_parsed', entries=len(data['features']))
    except Exception as error:
        result['error'] = str(error)[:250]
    return result

def main():
    integrations = json.loads((ROOT / 'integrations.json').read_text(encoding='utf-8'))
    selected = [r for r in integrations if r['method'] in ('rss', 'geojson') and r['endpoint_url']]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, selected))
    (ROOT / 'endpoint-probes.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    opml = ET.Element('opml', version='2.0')
    ET.SubElement(ET.SubElement(opml, 'head'), 'title').text = 'LarryToday - feeds parsed in audit'
    body = ET.SubElement(opml, 'body')
    for result in results:
        if result['status'] == 'feed_parsed':
            sid = next(r['source_id'] for r in selected if r['id'] == result['integration_id'])
            ET.SubElement(body, 'outline', text=sid, title=sid, type='rss', xmlUrl=result['url'])
    ET.indent(opml)
    ET.ElementTree(opml).write(ROOT / 'feeds.checked.opml', encoding='utf-8', xml_declaration=True)
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
