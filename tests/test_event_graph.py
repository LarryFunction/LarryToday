import unittest
from copy import deepcopy
from scripts.event_graph import build_event_views
from scripts.event_editor import validate

class EventGraphTests(unittest.TestCase):
    def row(self,id,title,day='2026-11-03',country='US',**kw):
        r={'id':id,'title':title,'title_zh':title,'summary_zh':'来源报道摘要','source_id':id,'source_name':id,'category':'国际政治','url':'https://example.com/'+id,'published_at':day+'T01:00:00Z','section':'本期新闻','geography':{'countries':[country],'kind':'single','code':country,'label':country}}
        r.update(kw);return r
    def edition(self,day,rows):return {'date':day,'revision':1,'articles':rows,'briefing':[{'article_id':r['id'],'event_id':'old-'+r['id'],'title':r['title'],'category':r['category'],'summary':'摘要'} for r in rows]}
    def test_event_preserves_all_reports_and_deduplicates_morning(self):
        rows=[self.row('a','US midterm elections: voters cast ballots'),self.row('b','美国中期选举：国会控制权之争')]
        original=deepcopy(rows);days,stories=build_event_views(editions=[self.edition('2026-11-03',rows)])
        events=days['2026-11-03']['events'];self.assertEqual(len(events),1)
        self.assertEqual(set(events[0]['article_ids']),{'a','b'})
        self.assertEqual(len(days['2026-11-03']['briefing']),1)
        self.assertEqual(rows,original)
    def test_stable_id_and_historical_day_does_not_leak_future(self):
        first=self.edition('2026-11-03',[self.row('a','US midterm elections: voters cast ballots')])
        second=self.edition('2026-11-04',[self.row('b','美国中期选举：结果陆续揭晓','2026-11-04')])
        days,tracks=build_event_views(editions=[first]);before=deepcopy(days)
        both,tracks=build_event_views(editions=[first,second])
        self.assertEqual(before['2026-11-03'],both['2026-11-03'])
        self.assertEqual(both['2026-11-03']['events'][0]['story_id'],both['2026-11-04']['events'][0]['story_id'])
        self.assertEqual(both['2026-11-04']['events'][0]['reporting_days'],2)
        self.assertEqual(len(next(iter(tracks.values()))['timeline']),2)
    def test_different_countries_are_not_same_riot(self):
        rows=[self.row('a','法国民众抗议养老金改革，街头示威持续',country='FR'),self.row('b','意大利民众抗议养老金改革，街头示威持续',country='IT')]
        days,tracks=build_event_views(editions=[self.edition('2026-11-03',rows)])
        self.assertEqual(len(days['2026-11-03']['events']),2)
        self.assertFalse(any(t['relations'] for t in tracks.values()))
    def test_explicit_relationship_is_attributed_not_merged(self):
        rows=[self.row('a','法国民众抗议养老金改革，街头示威持续',country='FR'),self.row('b','意大利民众抗议养老金改革，街头示威持续',country='IT',summary_zh='据报道，法国抗议浪潮蔓延至意大利，引发当地示威。')]
        days,tracks=build_event_views(editions=[self.edition('2026-11-03',rows)])
        self.assertEqual(len(days['2026-11-03']['events']),2)
        links=[r for t in tracks.values() for r in t['relations']]
        self.assertEqual(len(links),2)
        self.assertTrue(all(r['type']=='reported_connection' and r['article_id']=='b' and r['evidence'] in rows[1]['summary_zh'] for r in links))
    def test_distinct_research_papers_not_grouped_by_topic(self):
        rows=[self.row('a','Neural networks improve document parsing',research_status='preprint',url='https://arxiv.org/abs/2611.00001'),self.row('b','Neural networks improve document parsing',research_status='preprint',url='https://arxiv.org/abs/2611.00002')]
        # Existing identical-headline grouping must not override distinct paper identity.
        days,_=build_event_views(editions=[self.edition('2026-11-03',rows)])
        self.assertEqual(len(days['2026-11-03']['events']),2)
    def test_unknown_ids_and_fabricated_evidence_are_rejected(self):
        payload=[{'id':'a','title':'Nvidia CEO investigation','excerpt':'Source says investigation began'},{'id':'b','title':'Nvidia CEO investigation continues','excerpt':'Source reports more details'}]
        good={'title':'英伟达高管调查','members':[{'id':'a','evidence':'Nvidia CEO'},{'id':'b','evidence':'Nvidia CEO'}]}
        self.assertEqual(len(validate({'groups':[good]},payload)),1)
        bad=deepcopy(good);bad['members'][1]['id']='invented'
        self.assertFalse(validate({'groups':[bad]},payload))
        bad=deepcopy(good);bad['members'][1]['evidence']='made up quote'
        self.assertFalse(validate({'groups':[bad]},payload))
    def test_cross_year_elections_not_one_event(self):
        rows=[self.row('a','US midterm elections voting','2022-11-03'),self.row('b','US midterm elections voting','2026-11-03')]
        days,tracks=build_event_views(editions=[self.edition('2022-11-03',rows[:1]),self.edition('2026-11-03',rows[1:])])
        self.assertEqual(len(tracks),2)

    def test_reader_preserves_event_view_and_article_chunks(self):
        from scripts.build_pages import paged_payload
        rows=[self.row('a','US midterm elections voting'),self.row('b','美国中期选举：投票开始')]
        raw=self.edition('2026-11-03',rows);days,_=build_event_views(editions=[raw])
        raw.update(days[raw['date']]);manifest,chunks=paged_payload(raw)
        self.assertEqual(manifest['event_version'],2)
        self.assertEqual(len(manifest['events']),1)
        self.assertEqual({r['id'] for chunk in chunks for r in chunk},{'a','b'})
    def test_semantic_group_evidence_survives_into_dossier(self):
        assignment={'key':'semantic-test','title':'一次具体调查','evidence':'具体调查'}
        rows=[self.row('a','具体调查的最新进展',event_assignment=assignment),self.row('b','围绕具体调查的评论',event_assignment=assignment)]
        days,tracks=build_event_views(editions=[self.edition('2026-11-03',rows)])
        self.assertEqual(len(days['2026-11-03']['events']),1)
        self.assertEqual(next(iter(tracks.values()))['timeline'][0]['reports'][0]['event_assignment']['evidence'],'具体调查')

    def test_semantic_group_rejects_disjoint_local_disasters_and_generic_topics(self):
        payload=[{'id':'a','title':'移民船沉没救援行动','excerpt':'救援行动持续','countries':['GR']},{'id':'b','title':'移民船沉没救援行动','excerpt':'救援行动持续','countries':['SN']}]
        group={'title':'移民船沉没事件','members':[{'id':'a','evidence':'移民船沉没'},{'id':'b','evidence':'移民船沉没'}]}
        self.assertFalse(validate({'groups':[group]},payload))
        payload[1]['countries']=['GR']
        self.assertEqual(len(validate({'groups':[group]},payload)),1)
        group['title']='移民相关报道'
        self.assertFalse(validate({'groups':[group]},payload))
