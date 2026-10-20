import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from scripts import update_news
from scripts.update_news import parse_feed, validate_articles

class NewsTests(unittest.TestCase):
    def test_feed_dates_and_bad_links(self):
        xml=b'<rss><channel><item><title>Good &amp; safe</title><link>https://example.com/1</link><pubDate>Sun, 18 Oct 2026 07:00:00 +0800</pubDate></item><item><title>Bad</title><link>javascript:alert(1)</link></item></channel></rss>'
        rows=parse_feed(xml,'bbc','international')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['published_at'],'2026-10-17T23:00:00+00:00')
        self.assertEqual(rows[0]['title'],'Good & safe')

    def test_missing_date_not_fabricated(self):
        rows=parse_feed(b'<rss><item><title>x</title><link>https://example.com</link></item></rss>','x','x')
        self.assertIsNone(rows[0]['published_at'])

    def test_reject_entity(self):
        with self.assertRaises(ValueError): parse_feed(b'<!DOCTYPE rss><rss/>','x','x')

    def test_manual_rejects_unsafe_url_and_naive_date(self):
        row={'title':'x','url':'file:///etc/passwd','source_id':'x','category':'x'}
        with self.assertRaises(ValueError): validate_articles([row])
        row.update(url='https://example.com',published_at='2026-10-18T07:00:00')
        with self.assertRaises(ValueError): validate_articles([row])

    def test_failed_update_preserves_previous_edition(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            data=Path(temp)
            (data/'latest.json').write_text('{"previous":true}')
            with patch.object(update_news,'DATA',data), patch('scripts.collect.collect',return_value=([],[])),patch('scripts.collect.collect_social'):
                with self.assertRaises(RuntimeError): update_news.publish()
            self.assertEqual(json.loads((data/'latest.json').read_text()),{'previous':True})
            self.assertFalse((data/'.update.lock').exists())

    def test_manual_publish_archives_and_deduplicates(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            data=Path(temp)
            row={'title':'News','url':'https://example.com/news','source_id':'bbc','category':'国际政治','published_at':'2026-10-17T20:00:00+00:00'}
            source=data/'manual.json'
            source.write_text(json.dumps([row,row]))
            with patch.object(update_news,'DATA',data): result=update_news.publish(source,ai=False,edition_date='2026-10-18')
            self.assertEqual(result['count'],1)
            self.assertTrue((data/'editions'/f"{result['date']}.json").exists())
            self.assertEqual(json.loads((data/'archive.json').read_text()),[result['date']])

if __name__=='__main__': unittest.main()
