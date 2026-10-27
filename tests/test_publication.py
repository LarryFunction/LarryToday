import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import timedelta
from scripts.editorial import events, window, timestamp
from scripts.build_pages import paged_payload
from scripts.publication_report import publication_report
from scripts import update_news

class PublicationTests(unittest.TestCase):
    def row(self,id='a',**kw):
        result={'id':id,'title':'France parliament approves new climate emissions law','source_id':id,'category':'国际政治','published_at':window()['start'],'url':'https://example.com/'+id,'section':'本期新闻'}
        result.update(kw);return result

    def test_same_headline_preserves_sources_and_no_extra_ai(self):
        rows=[self.row(),self.row('b')]
        group=events(rows,[])
        self.assertEqual(len(group),1)
        self.assertEqual(set(group[0]['article_ids']),{'a','b'})
        self.assertEqual(group[0]['grouping_basis'],'identical_headline')

    def test_distinct_progress_numbers_and_dates_do_not_merge(self):
        base=self.row()
        for other in [self.row('b',title=base['title']+' rejected'),self.row('b',title=base['title']+' 2027'),self.row('b',published_at=(timestamp(base['published_at'])+timedelta(hours=13)).isoformat()),self.row('b',source_id='a')]:
            self.assertEqual(len(events([base,other],[])),2)

    def test_reader_relinks_briefing_without_dropping_articles(self):
        edition={'articles':[self.row(),self.row('b')],'events':[], 'briefing':[{'article_id':'a','event_id':'old'}]}
        manifest,chunks=paged_payload(edition)
        self.assertEqual(len(manifest['events']),1)
        self.assertEqual(manifest['briefing'][0]['event_id'],manifest['events'][0]['id'])
        self.assertEqual(sum(map(len,chunks)),2)
        self.assertEqual(edition['briefing'][0]['event_id'],'old')

    def test_background_only_keeps_previous_edition_without_paid_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp); old='{"date":"2020-01-01","articles":[]}'
            (data/'latest.json').write_text(old,encoding='utf-8')
            row=self.row(published_at=(timestamp(window()['start'])-timedelta(hours=1)).isoformat())
            with patch.object(update_news,'DATA',data),patch('scripts.collect.collect',return_value=([row],[{'ok':True}])),patch('scripts.collect.collect_social'),patch('scripts.ai_news.enrich') as ai:
                with self.assertRaises(RuntimeError):update_news.publish()
                ai.assert_not_called()
            self.assertEqual((data/'latest.json').read_text(encoding='utf-8'),old)
            self.assertEqual(json.loads((data/'update-report.json').read_text(encoding='utf-8'))['state'],'failed')
            self.assertFalse((data/'.update.lock').exists())

    def test_ai_failure_still_publishes_readable_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)
            with patch.object(update_news,'DATA',data),patch('scripts.collect.collect',return_value=([self.row()],[{'ok':True}])),patch('scripts.collect.collect_social'),patch('scripts.ai_news.enrich',side_effect=RuntimeError('secret must not appear')):
                update_news.publish()
            self.assertEqual(len(json.loads((data/'latest.json').read_text(encoding='utf-8'))['articles']),1)
            report=(data/'update-report.json').read_text(encoding='utf-8')
            self.assertNotIn('secret',report)
            self.assertEqual(json.loads(report)['state'],'degraded')

    def test_unknown_usage_not_zero(self):
        report=publication_report({'date':'2020-01-01','articles':[],'events':[],'ai_status':{'state':'disabled'}},0)
        self.assertIsNone(report['prompt_tokens'])

if __name__=='__main__':unittest.main()
