import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_pages import ROOT, build_site


class PagesBuildTests(unittest.TestCase):
    def test_static_site_contains_pages_and_api(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'dist'
            result = build_site(ROOT, out)

            self.assertTrue((out / 'index.html').exists())
            self.assertTrue((out / 'style.css').exists())
            self.assertTrue((out / 'app.js').exists())
            self.assertTrue((out / '.nojekyll').exists())
            background=json.loads((out / 'api/background-context.json').read_text(encoding='utf-8'))
            self.assertGreaterEqual(len(background['items']),10)
            self.assertFalse((out / '.env').exists())
            self.assertGreater(result['editions'], 0)
            self.assertGreater(result['sources'], 0)

            news = json.loads((out / 'api/news.json').read_text(encoding='utf-8'))
            self.assertIn('articles', news)
            sources = json.loads((out / 'api/sources.json').read_text(encoding='utf-8'))
            self.assertGreaterEqual(len(sources['sources']), 367)
            archive = json.loads((out / 'api/archive.json').read_text(encoding='utf-8'))
            self.assertTrue(archive)

            for day in archive:
                self.assertTrue((out / 'api/editions' / f'{day}.json').exists())
                self.assertTrue((out / 'api/revisions' / f'{day}.json').exists())

            app = (out / 'app.js').read_text(encoding='utf-8')
            self.assertIn("get('api/news.json')", app)
            self.assertNotIn("get('/api/news')", app)
            self.assertIn("'force-cache':'no-cache'", app)
            reader=json.loads((out / 'api/reader.json').read_text(encoding='utf-8'))
            for row in reader['articles']:self.assertTrue((out / row['_chunk']).exists())


if __name__ == '__main__':
    unittest.main()
