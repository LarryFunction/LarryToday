import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.ai_news import Client, BudgetExceeded, candidate_groups, enrich
from scripts.geography import geography
from scripts.build_pages import paged_payload


class ReadingCostTests(unittest.TestCase):
    def test_geography_uses_content_not_publisher(self):
        self.assertEqual(geography({'title': 'New algorithm', 'source_region': '美国'})['kind'], 'unknown')
        self.assertEqual(geography({'title': 'China and United States agree'})['countries'], ['CN', 'US'])
        self.assertEqual(geography({'title': 'New algorithm', 'research_status': 'preprint'})['code'], 'RESEARCH')
        self.assertEqual(geography({'title': 'Global climate report'})['code'], 'WORLD')

    def test_chunk_index_preserves_all_articles_and_search(self):
        rows=[{'id':str(i), 'title':'Title', 'summary_zh':'可检索摘要', 'feed_excerpt':'x'*4000} for i in range(65)]
        manifest,chunks=paged_payload({'date':'2026-10-20','articles':rows})
        self.assertEqual([len(c) for c in chunks], [30,30,5])
        self.assertEqual([r['id'] for c in chunks for r in c], [r['id'] for r in rows])
        self.assertNotIn('feed_excerpt',manifest['articles'][0])
        self.assertIn('可检索摘要',manifest['articles'][0]['_search'])
        self.assertEqual(manifest['articles'][30]['_chunk'],'api/chunks/1.json')

    def test_zero_budget_makes_no_generation_request(self):
        client=Client({'BASE_URL':'https://example.com','BASE_KEY_1':'test','BASE_KEY_2':'test','BASE_KEY_3':'test','AI_TOKEN_BUDGET':'0'})
        with patch.object(client.opener,'open') as network:
            with self.assertRaises(BudgetExceeded): client.chat(0,'prompt',[])
            network.assert_not_called()

    def test_usage_settles_reserved_tokens(self):
        client=Client({'BASE_URL':'https://example.com','BASE_KEY_1':'test','BASE_KEY_2':'test','BASE_KEY_3':'test'})
        body={'usage':{'prompt_tokens':123,'completion_tokens':45},'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]}
        with patch.object(client.opener,'open') as network:
            network.return_value.__enter__.return_value.read.return_value=json.dumps(body).encode()
            client.chat(2,'prompt',[])
        self.assertEqual(client.used_bound,168)
        self.assertEqual(client.usage['stages']['compare']['prompt_tokens'],123)

    def test_candidates_require_overlap_and_multiple_sources(self):
        rows=[
            {'id':'a','source_id':'one','title':'France parliament approves climate emissions law','published_at':'2026-10-20T03:00:00Z'},
            {'id':'b','source_id':'two','title':'France parliament passes climate emissions law','published_at':'2026-10-20T04:00:00Z'},
            {'id':'c','source_id':'three','title':'New neural networks improve image classification','published_at':'2026-10-20T04:00:00Z'}]
        self.assertEqual([[r['id'] for r in g] for g in candidate_groups(rows)], [['a','b']])
        self.assertEqual(candidate_groups(rows,0),[])
        self.assertEqual(candidate_groups([rows[0],dict(rows[1],source_id='one')]),[])

    def test_budget_keeps_every_original_article(self):
        config={'BASE_URL':'https://example.com','BASE_KEY_1':'test','BASE_KEY_2':'test','BASE_KEY_3':'test','AI_MODEL':'test','AI_TOKEN_BUDGET':'0'}
        rows=[{'id':str(i),'title':'Title','category':'科技与 AI','source_id':'source','published_at':'2026-10-20T03:00:00Z'} for i in range(20)]
        with tempfile.TemporaryDirectory() as directory, patch('scripts.ai_news.settings',return_value=config), patch.object(Client,'discover',return_value=['test']):
            result,comparisons,stats=enrich(rows,Path(directory))
        self.assertEqual(len(result),20)
        self.assertEqual(stats['remaining'],20)
        self.assertTrue(stats['budget_exhausted'])
        self.assertEqual(stats['usage']['calls'],0)

    def test_daily_skips_existing_edition_without_ai(self):
        from scripts import daily_update
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'data/editions').mkdir(parents=True)
            (root/'data/editions/2026-10-20.json').write_text('{}')
            with patch.object(daily_update,'ROOT',root), patch.object(daily_update,'window',return_value={'date':'2026-10-20'}), patch.object(daily_update,'publish') as publish:
                daily_update.run()
                publish.assert_not_called()

    def test_reserves_comparison_budget(self):
        client=Client({'BASE_URL':'https://example.com','BASE_KEY_1':'test','BASE_KEY_2':'test','BASE_KEY_3':'test','AI_TOKEN_BUDGET':'10000'})
        client.editorial_budget=0
        with patch.object(client.opener,'open') as network:
            with self.assertRaises(BudgetExceeded): client.chat(0,'prompt',[])
            network.assert_not_called()
            network.return_value.__enter__.return_value.read.return_value=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]}).encode()
            client.chat(2,'prompt',[])
            self.assertEqual(client.usage['missing_usage'],1)


if __name__ == '__main__':
    unittest.main()
