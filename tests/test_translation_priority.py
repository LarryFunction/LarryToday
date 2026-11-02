import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.ai_news import Client, enrich

CONFIG={'BASE_URL':'https://example.com','BASE_KEY_1':'test','BASE_KEY_2':'test','BASE_KEY_3':'test','AI_MODEL':'test','AI_COMPARISON_LIMIT':'0'}

class TranslationPriorityTests(unittest.TestCase):
    def rows(self):
        return [{'id':str(i),'title':'English news','feed_excerpt':'Original summary','category':'科技与 AI','source_id':'one'} for i in range(2)]

    def test_retry_only_missing_items_and_then_edit(self):
        rows=self.rows(); calls=[]
        def translate(client,batch):
            calls.append([r['id'] for r in batch])
            r=batch[0]
            return {r['id']:{'title_zh':'中文标题','summary_zh':'中文摘要'}}
        with tempfile.TemporaryDirectory() as directory, patch('scripts.ai_news.settings',return_value=CONFIG), patch.object(Client,'discover'), patch('scripts.ai_news.translate_batch',side_effect=translate), patch('scripts.ai_news.edit_batch',return_value={}):
            result,_,stats=enrich(rows,Path(directory))
        self.assertEqual(calls,[['0','1'],['1']])
        self.assertEqual(stats['basic_translated'],2)
        self.assertEqual(stats['remaining'],0)
        self.assertEqual(len(result),2)

    def test_two_failed_attempts_keep_original_and_skip_detail(self):
        with tempfile.TemporaryDirectory() as directory, patch('scripts.ai_news.settings',return_value=CONFIG), patch.object(Client,'discover'), patch('scripts.ai_news.translate_batch',return_value={}) as translate, patch('scripts.ai_news.edit_batch') as detail:
            result,_,stats=enrich(self.rows(),Path(directory))
        self.assertEqual(translate.call_count,2)
        detail.assert_not_called()
        self.assertEqual(stats['remaining'],2)
        self.assertEqual(result[0]['title'],'English news')

    def test_published_translation_reused_without_cache_or_calls(self):
        row=dict(self.rows()[0],title_zh='中文标题',title_en='English news',summary_zh='中文摘要',tags=['新闻'])
        with tempfile.TemporaryDirectory() as directory, patch('scripts.ai_news.settings',return_value=CONFIG), patch.object(Client,'discover'), patch.object(Client,'chat') as chat:
            result,_,stats=enrich([row],Path(directory))
        chat.assert_not_called()
        self.assertEqual(stats['cached'],1)
        self.assertEqual(result[0]['summary_zh'],'中文摘要')
