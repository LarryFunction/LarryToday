import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scripts import update_news
from scripts.editorial import window
from scripts.ai_news import Client,BudgetExceeded

class PublicationGateTests(unittest.TestCase):
    def row(self):
        return {'id':'a','title':'A new discovery','feed_excerpt':'Researchers report results','url':'https://example.com/a','source_id':'one','category':'科学与探索','published_at':window()['start']}

    def test_pending_retains_all_news_and_resumes_without_recrawl(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp);old='{"date":"2020-01-01","articles":[]}'
            (data/'latest.json').write_text(old,encoding='utf-8')
            with patch.object(update_news,'DATA',data),patch('scripts.collect.collect',return_value=([self.row()],[{'ok':True}])),patch('scripts.collect.collect_social'):
                result=update_news.publish(ai=False,edition_date=window()['date'],require_complete=True)
            self.assertEqual(result['state'],'pending_translation')
            self.assertEqual((data/'latest.json').read_text(encoding='utf-8'),old)
            pending=data/'pending'/f"{window()['date']}.json"
            self.assertEqual(len(json.loads(pending.read_text(encoding='utf-8'))['articles']),1)
            def translated(rows,*args):
                rows[0].update(title_zh='研究的新发现',summary_zh='研究者报告了一项新发现。')
                return rows,[],{'state':'complete'}
            with patch.object(update_news,'DATA',data),patch('scripts.collect.collect') as collect,patch('scripts.ai_news.enrich',side_effect=translated):
                result=update_news.publish(edition_date=window()['date'],require_complete=True)
                collect.assert_not_called()
            self.assertFalse(pending.exists())
            self.assertEqual(len(json.loads((data/'latest.json').read_text(encoding='utf-8'))['articles']),1)

    def test_shared_ledger_survives_client_restart_and_stops_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'BASE_URL':'https://example.com','BASE_KEY_1':'x','BASE_KEY_2':'y','BASE_KEY_3':'z','AI_TOKEN_BUDGET':'5000','AI_DAILY_LEDGER':str(Path(tmp)/'ledger.json')}
            client=Client(config);client.used_bound=4900;client.persist_budget()
            second=Client(config)
            self.assertEqual(second.used_bound,4900)
            with patch.object(second.opener,'open') as network:
                with self.assertRaises(BudgetExceeded):second.chat(0,'translate',[],max_tokens=1000)
                network.assert_not_called()
            ledger=json.loads(Path(config['AI_DAILY_LEDGER']).read_text())
            ledger['date']='2020-01-01';Path(config['AI_DAILY_LEDGER']).write_text(json.dumps(ledger))
            self.assertEqual(Client(config).used_bound,0)

    def test_reservation_is_persisted_before_network_and_settled(self):
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'ledger.json'
            config={'BASE_URL':'https://example.com','BASE_KEY_1':'x','BASE_KEY_2':'y','BASE_KEY_3':'z','AI_TOKEN_BUDGET':'50000','AI_DAILY_LEDGER':str(path)}
            client=Client(config)
            response=MagicMock()
            response.__enter__.return_value.read.return_value=json.dumps({'usage':{'prompt_tokens':100,'completion_tokens':30}}).encode()
            def open_request(*args,**kwargs):
                self.assertGreater(json.loads(path.read_text())['used'],130)
                return response
            with patch.object(client.opener,'open',side_effect=open_request):
                client.request('/chat/completions',0,{'max_tokens':1000})
            self.assertEqual(json.loads(path.read_text())['used'],130)
            self.assertEqual(Client(config).used_bound,130)

    def test_missing_summary_also_blocks_publication(self):
        from scripts.update_news import translation_gap
        self.assertEqual(translation_gap([{'title_zh':'中文标题','feed_excerpt':'English summary'}]),1)
        self.assertEqual(translation_gap([{'title':'中文标题','feed_excerpt':'中文摘要'}]),0)

    def test_daily_captures_today_before_resuming_backlog(self):
        import os
        from scripts import daily_update
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/pending').mkdir(parents=True)
            (root/'data/pending/2026-11-03.json').write_text('{}')
            calls=[]
            def publish(**kwargs):
                calls.append(kwargs)
                return {'date':kwargs['edition_date'],'count':1,'state':'pending_translation'}
            with patch.object(daily_update,'ROOT',root),patch.object(daily_update,'window',return_value={'date':'2026-11-04'}),patch.object(daily_update,'publish',side_effect=publish),patch.dict(os.environ,{'AI_ENABLED':'false'}):
                daily_update.run()
            self.assertEqual(calls[0]['edition_date'],'2026-11-04')
            self.assertFalse(calls[0]['ai'])
            self.assertEqual(calls[1]['edition_date'],'2026-11-03')
            self.assertTrue(all(c['require_complete'] for c in calls))
