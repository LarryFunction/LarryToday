import unittest
from scripts.ai_news import clean_editorial, clean_comparisons, Client
from scripts.update_news import excerpt

class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'id':'a','source_id':'bbc'},{'id':'b','source_id':'guardian'}]
        self.item={'id':'a','title_zh':'标题','title_en':'Title','summary_zh':'概述','tags':['科技'],'grounded':True}

    def test_editorial_requires_complete_and_reviewed_evidence(self):
        self.assertIn('a',clean_editorial({'articles':[self.item]},self.rows[:1]))
        with self.assertRaises(ValueError): clean_editorial({'articles':[self.item]},self.rows)
        with self.assertRaises(ValueError): clean_editorial({'articles':[dict(self.item,grounded=False)]},self.rows[:1])
        with self.assertRaises(ValueError): clean_editorial({'articles':[dict(self.item,id='made-up')]},self.rows[:1])

    def test_comparison_requires_two_sources_and_real_references(self):
        group={'same_event':True,'article_ids':['a','b'],'title_zh':'事件','common_ground':'报道了同一事件','differences':[{'article_id':'a','focus':'时间'},{'article_id':'b','focus':'地点'}]}
        self.assertEqual(len(clean_comparisons({'comparisons':[group]},self.rows)),1)
        self.assertEqual(clean_comparisons({'comparisons':[group]},[self.rows[0],dict(self.rows[1],source_id='bbc')]),[])
        self.assertEqual(clean_comparisons({'comparisons':[dict(group,article_ids=['a','invented'])]},self.rows),[])
        self.assertEqual(clean_comparisons({'comparisons':[dict(group,same_event=False)]},self.rows),[])

    def test_excerpt_removes_markup_and_script(self):
        self.assertEqual(excerpt('<p>Actual &amp; text</p><script>fake()</script>'),'Actual & text')

    def test_reject_insecure_or_embedded_credentials(self):
        for base in ['http://example.com','https://user:pass@example.com','https://example.com?key=secret']:
            with self.assertRaises(ValueError): Client({'BASE_URL':base})

if __name__=='__main__': unittest.main()
