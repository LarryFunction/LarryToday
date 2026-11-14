import unittest
from unittest.mock import patch
from scripts.source_evidence import discover, publisher, public_url, relevant

class SourceEvidenceTests(unittest.TestCase):
    def test_domain_boundary_and_private_network_block(self):
        ps=[{'name':'Example','domains':['example.org']}]
        self.assertEqual(publisher('https://news.example.org/a',ps),'Example')
        self.assertIsNone(publisher('https://example.org.evil.test/a',ps))
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(ValueError):public_url('https://example.org')
        with self.assertRaises(ValueError):public_url('file:///private')
    def edition(self):
        rows=[{'id':i,'title':'Acme lunar mission launch investigation','title_en':'Acme lunar mission launch investigation','title_zh':'月球任务发射调查','source_id':i,'url':'https://press.example/'+i,'content_type':'新闻'} for i in ['a','b']]
        return {'date':'2026-11-14','articles':rows,'events':[{'id':'event-1','lead_id':'a','article_ids':['a','b'],'title':'月球任务发射调查'}],'briefing':[]}
    def test_search_snippet_not_evidence_and_off_topic_page_rejected(self):
        def fetch(url):
            if 'bing.com' in url:return '<rss><channel><item><title>Acme lunar mission launch investigation</title><description>Invented conclusion</description><link>https://acme.example/news</link></item></channel></rss>',url
            if 'acme.example' in url:return '<title>Acme company home</title><p>Welcome</p>',url
            return '<html><a href="https://acme.example/news">statement</a></html>',url
        data=discover(self.edition(),[{'name':'Acme','domains':['acme.example'],'aliases':['Acme']}],fetch)
        self.assertFalse(data['events'][0]['materials'])
        self.assertNotIn('Invented conclusion',str(data))
    def test_retrieved_primary_page_retains_attribution(self):
        def fetch(url):
            if 'bing.com' in url:return '<rss><channel/></rss>',url
            if 'acme.example' in url:return '<title>Acme lunar mission launch investigation</title><p>Acme lunar mission launch investigation remains underway.</p>',url
            return '<a href="https://acme.example/news">statement</a>',url
        d=discover(self.edition(),[{'name':'Acme','domains':['acme.example'],'aliases':['Acme']}],fetch)
        m=d['events'][0]['materials'][0]
        self.assertEqual(m['publisher'],'Acme');self.assertEqual(m['status'],'retrieved');self.assertNotIn('verified',m)
        self.assertLessEqual(d['requests'],8)
    def test_outage_is_not_absence_of_evidence(self):
        def fetch(url):raise TimeoutError()
        d=discover(self.edition(),[],fetch)
        self.assertEqual(d['events'][0]['status'],'retrieval_unavailable')
