import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.ai_news import clean_editorial, enrich, Client, VERSION, evidence
from scripts.geography import geography, clean_country_mentions, TOPICS
from scripts.editorial import classify

class GeographyTests(unittest.TestCase):
    def test_ai_city_evidence_and_country_order(self):
        row={'title':'Paris and Berlin discuss transport','country_mentions':[{'code':'FR','evidence':'Paris'},{'code':'DE','evidence':'Berlin'}]}
        self.assertEqual(geography(row)['countries'],['FR','DE'])
        self.assertEqual(geography(row)['kind'],'pair')

    def test_bad_optional_ai_field_falls_back_without_losing_article(self):
        row={'id':'a','title':'China releases report'}
        item={'id':'a','title_zh':'报告','title_en':'Report','summary_zh':'摘要','tags':['报告'],'grounded':True}
        for mentions in ([{'code':'XX','evidence':'China'}],[{'code':'US','evidence':'not in source'}],'US',[{'code':[], 'evidence':'China'}]):
            result=clean_editorial({'articles':[dict(item,country_mentions=mentions)]},[row])['a']
            self.assertNotIn('country_mentions',result)
            self.assertEqual(geography(dict(row,**result))['countries'],['CN'])

    def test_empty_ai_result_uses_theme_not_incidental_country(self):
        row={'title':'Global software launched by US company','category':'科技与 AI','country_mentions':[]}
        self.assertEqual(geography(row)['code'],'WORLD')
        self.assertEqual(geography(row)['countries'],[])

    def test_all_sections_have_named_topic_fallback(self):
        for category,(code,label) in TOPICS.items():
            mark=geography({'title':'New developments','category':category})
            self.assertEqual((mark['code'],mark['label'],mark['kind']),(code,label,'topic'))
        self.assertEqual(geography({'title':'New theory','source_kind':'research'})['label'],'科学研究')

    def test_theme_follows_final_category(self):
        row=classify({'title':'New artificial intelligence algorithm','category':'国际政治','url':'https://example.com/story'})
        self.assertEqual(row['geography']['code'],'TECH')

    def test_legacy_cache_is_reused_without_generation(self):
        config={'BASE_URL':'https://example.com','BASE_KEY_1':'test','BASE_KEY_2':'test','BASE_KEY_3':'test','AI_MODEL':'test'}
        row={'id':'a','title':'New algorithm','category':'科技与 AI','source_id':'one'}
        old={'title_zh':'新算法','title_en':'New algorithm','summary_zh':'算法介绍','tags':['算法']}
        key=hashlib.sha256(json.dumps([VERSION,'test',evidence(row)],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            cache=Path(directory)/'ai-cache';cache.mkdir()
            (cache/(key+'.json')).write_text(json.dumps(old),encoding='utf-8')
            with patch('scripts.ai_news.settings',return_value=config),patch.object(Client,'discover'),patch.object(Client,'chat') as chat:
                rows,_,stats=enrich([row],Path(directory))
                chat.assert_not_called()
                self.assertEqual(stats['cached'],1)
                self.assertEqual(rows[0]['title_zh'],'新算法')

if __name__=='__main__': unittest.main()
