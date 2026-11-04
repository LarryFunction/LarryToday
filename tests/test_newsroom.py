import json
import unittest
from unittest.mock import patch
from scripts.editorial import classify,events
from scripts.newsroom import article_tags,select_briefing
from scripts.ai_news import Client

class NewsroomTests(unittest.TestCase):
    def row(self,id,title,source='one',**kw):
        r={'id':id,'title':title,'category':'国际政治','source_id':source,'url':'https://example.com/world/'+id,'published_at':'2026-11-03T01:00:00Z'}
        r.update(kw);return classify(r)

    def test_board_game_is_culture_without_inventing_country(self):
        r=self.row('game','This legendary board game could take decades to complete')
        self.assertEqual(r['category'],'社会与文化')
        self.assertEqual(r['geography']['code'],'CULTURE')
        self.assertIn('桌游',r['tags'])

    def test_tags_exist_and_preserve_valid_editorial_tags(self):
        r=self.row('a','New OpenAI model',tags=['模型评测','模型评测'])
        self.assertIn('模型评测',r['tags'])
        self.assertIn('人工智能',r['tags'])
        self.assertEqual(len(r['tags']),len(set(r['tags'])))
        self.assertTrue(article_tags(self.row('b','Unclassified report')))

    def test_major_event_beats_routine_research_and_games(self):
        rows=[self.row('a','New paper on language models',source_kind='research',research_status='preprint'),self.row('b','Legendary board game challenge'),self.row('c','Earthquake forces state of emergency')]
        picks=select_briefing(rows,events(rows,[]),1)
        self.assertEqual(picks[0][0]['id'],'c')
        self.assertEqual(picks[0][1]['social_heat'],'unavailable')

    def test_wire_reprints_are_not_independent_attention(self):
        rows=[self.row('a','Central bank announces interest rate cut','one',upstream_agency='wire'),self.row('b','Central bank announces interest rate cut','two',upstream_agency='wire')]
        picks=select_briefing(rows,events(rows,[]))
        self.assertTrue(all(reason['independent_sources']==1 for _,reason in picks))

    def test_ai_morning_requires_known_id_and_literal_evidence(self):
        from scripts.ai_news import choose_morning
        from unittest.mock import Mock
        rows=[self.row('a','Earthquake forces state of emergency')]
        client=Mock()
        client.chat.return_value={'picks':[{'id':'invented','reason':'重要','evidence':'Earthquake'}, {'id':'a','reason':'影响公共安全','evidence':'not in the evidence'}]}
        self.assertEqual(choose_morning(client,rows),0)
        client.chat.return_value={'picks':[{'id':'a','reason':'影响公共安全','evidence':'Earthquake'}]}
        self.assertEqual(choose_morning(client,rows),1)
        self.assertEqual(rows[0]['editorial_pick']['basis'],'ai_shortlist')

    def test_budget_estimate_is_bounded_and_monotonic(self):
        from scripts.budget_model import estimate
        self.assertLess(estimate(200),estimate(1000))
        self.assertEqual(estimate(1036),430000)

    def test_simple_deepseek_request_disables_thinking(self):
        c=Client({'BASE_URL':'https://example.com','BASE_KEY_1':'x','BASE_KEY_2':'y','BASE_KEY_3':'z','AI_MODEL':'deepseek-flash'})
        response={'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]}
        with patch.object(c,'request',return_value=response) as request:
            c.chat(0,'translate',[])
        self.assertEqual(request.call_args.args[2]['thinking'],{'type':'disabled'})
        c.model='other-provider'
        with patch.object(c,'request',return_value=response) as request:c.chat(0,'translate',[])
        self.assertNotIn('thinking',request.call_args.args[2])
