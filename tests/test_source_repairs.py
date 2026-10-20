import io
import json
import socket
import ssl
import unittest
import urllib.error
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from scripts.update_news import parse_feed
from scripts.collect import error_details
from scripts.news_pages import article_links, parse_article
from scripts.social import fetch_accounts
from scripts.editorial import classify


class MetadataTests(unittest.TestCase):
    def test_atom_published_not_updated_and_author_doi(self):
        xml=b'''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:a="http://arxiv.org/schemas/atom"><entry>
        <updated>2026-10-19T13:00:00Z</updated><published>2026-10-01T12:00:00Z</published>
        <title>Review of models</title><link href="http://arxiv.org/abs/2610.00001v2"/>
        <author><name>A Researcher</name></author><a:doi>10.1/test</a:doi></entry></feed>'''
        r=parse_feed(xml,'arxiv','科技与 AI')[0]
        self.assertEqual(r['published_at'],'2026-10-01T12:00:00+00:00')
        self.assertEqual(r['updated_at'],'2026-10-19T13:00:00+00:00')
        self.assertEqual(r['authors'],['A Researcher'])
        self.assertEqual(r['doi'],'10.1/test')
        self.assertEqual(classify(r)['content_type'],'预印本')

    def test_date_only_rdf_retained_without_midnight(self):
        xml=b'''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/"><item><title>Paper</title><link>https://example.org/paper</link><dc:date>2026-10-19</dc:date><dc:creator>A</dc:creator></item></rdf:RDF>'''
        r=parse_feed(xml,'nature','科学与探索')[0]
        self.assertIsNone(r['published_at'])
        self.assertEqual(r['published_day'],'2026-10-19')
        self.assertEqual(r['authors'],['A'])

    def test_updated_only_does_not_become_publication(self):
        xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>T</title><link href="https://example.org"/><updated>2026-10-19T10:00:00Z</updated></entry></feed>'
        self.assertIsNone(parse_feed(xml,'x','x')[0]['published_at'])

    def test_parse_error_code_is_not_http_status(self):
        import xml.etree.ElementTree as ET
        try: ET.fromstring('<')
        except ET.ParseError as e:
            self.assertIsNone(error_details(e)['http_status'])
            self.assertEqual(error_details(e)['error_kind'],'parse_or_validation')
        for reason,kind in [(socket.gaierror(),'dns'),(ssl.SSLError(),'tls'),(TimeoutError(),'timeout')]:
            self.assertEqual(error_details(urllib.error.URLError(reason))['error_kind'],kind)

    def test_news_header_and_attribution(self):
        r=parse_article('<title>标题-新华网</title><meta name="publishdate" content="2026-10-19"><meta name="source" content="人民日报"><span class="time">08:30:15</span>','https://www.news.cn/a')
        self.assertEqual(r['published_at'],'2026-10-19T00:30:15+00:00')
        self.assertEqual(r['attribution'],'人民日报')
        self.assertNotIn('upstream_agency',r)
        with self.assertRaises(ValueError): parse_article('<title>T</title><meta name="publishdate" content="2026-10-19">','https://www.news.cn/a')

    def test_article_host_allowlist(self):
        suffix='/politics/20261019/'+'a'*32+'/c.html'
        links=article_links('<a href="https://evil.test'+suffix+'">x</a><a href="'+suffix+'">ok</a>','https://www.news.cn/politics/')
        self.assertEqual(links,['https://www.news.cn'+suffix])

    def test_arxiv_replacement_rss_metadata(self):
        xml=b'''<rss xmlns:a="http://arxiv.org/schemas/atom"><channel><item><title>Paper</title><link>https://arxiv.org/abs/2610.00001</link><pubDate>Mon, 19 Oct 2026 00:00:00 -0400</pubDate><description>arXiv:2610.00001v2 Announce Type: replace Abstract: Text</description><a:DOI>10.1/paper</a:DOI><a:journal_reference>Journal</a:journal_reference></item></channel></rss>'''
        row=parse_feed(xml,'arxiv','科技与 AI')[0]
        self.assertEqual(row['doi'],'10.1/paper')
        self.assertEqual(row['paper_version'],2)
        self.assertEqual(row['date_basis'],'rss_announcement')
        self.assertEqual(classify(row)['content_type'],'预印本修订')


class SocialTests(unittest.TestCase):
    def config(self,**kwargs):
        return {'accounts':[{'username':'tester','name':'Tester','identity_status':'manually_verified',**kwargs}]}
    def opener(self,*bodies):
        return Mock(open=Mock(side_effect=[io.BytesIO(json.dumps(b).encode()) for b in bodies]))
    def identity(self): return {'data':{'id':'123','username':'tester'}}
    def post(self,id):
        return {'id':id,'text':'Opinion','author_id':'123','created_at':datetime.now(timezone.utc).isoformat()}
    def test_identity_gate_does_not_call_api(self):
        opener=Mock()
        p,s,c=fetch_accounts(self.config(identity_status='user_supplied_unverified'),'secret',opener,{})
        self.assertEqual(s[0]['state'],'identity_required');opener.open.assert_not_called()
    def test_pagination_and_incremental_checkpoint(self):
        op=self.opener(self.identity(),{'data':[self.post('200')],'meta':{'next_token':'next'}},{'data':[self.post('199')],'meta':{}})
        p,s,c=fetch_accounts(self.config(),'secret',op,{'123':'100'})
        self.assertEqual(len(p),2);self.assertEqual(c['123'],'200')
        self.assertIn('since_id=100',op.open.call_args_list[1].args[0].full_url)
        self.assertIn('pagination_token=next',op.open.call_args_list[2].args[0].full_url)
    def test_page_limit_keeps_old_checkpoint(self):
        op=self.opener(self.identity(),{'data':[self.post('200')],'meta':{'next_token':'next'}})
        p,s,c=fetch_accounts({**self.config(),'max_pages_per_account':1},'secret',op,{'123':'100'})
        self.assertEqual(c['123'],'100');self.assertEqual(s[0]['state'],'coverage_limited')
    def test_errors_are_not_empty_success(self):
        for code,state in [(401,'unauthorized'),(403,'forbidden'),(429,'rate_limited')]:
            op=Mock(open=Mock(side_effect=urllib.error.HTTPError('https://api.x.com',code,'SECRET',{},None)))
            p,s,c=fetch_accounts(self.config(),'secret',op,{})
            self.assertEqual(s[0]['state'],state);self.assertNotIn('SECRET',json.dumps(s))
        op=self.opener(self.identity(),{'errors':[{'detail':'private'}]})
        p,s,c=fetch_accounts(self.config(),'secret',op,{})
        self.assertEqual(s[0]['state'],'unavailable')
    def test_id_mismatch(self):
        p,s,c=fetch_accounts(self.config(user_id='999'),'secret',self.opener(self.identity()),{})
        self.assertEqual(s[0]['state'],'identity_mismatch')


class CollectionIntegrationTests(unittest.TestCase):
    def test_author_feed_stays_out_of_news_pool_and_survives_x_disabled(self):
        from scripts import collect
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);(root/'config').mkdir();data=root/'data'
            feed=dict(id='author',source_id='author',name='Author',region='Global',category='科技与 AI',url='https://example.org/feed',enabled=True,family='author',kind='opinion')
            (root/'config/feeds.json').write_text(json.dumps([feed]),encoding='utf-8')
            (root/'config/social.json').write_text('{"enabled":false,"accounts":[]}',encoding='utf-8')
            date=datetime.now(timezone.utc).isoformat()
            xml=f'<rss><channel><item><title>Opinion</title><link>https://example.org/post</link><pubDate>{date}</pubDate></item></channel></rss>'.encode()
            with patch.object(collect,'ROOT',root),patch('urllib.request.urlopen',return_value=io.BytesIO(xml)),patch('scripts.ai_news.settings',return_value={}):
                rows,states=collect.collect(data)
                self.assertEqual(rows,[])
                self.assertEqual(states[0]['state'],'available')
                status=collect.collect_social(data)
                self.assertEqual(status['state'],'disabled')
                posts=json.loads((data/'social-posts.json').read_text(encoding='utf-8'))
                self.assertEqual(len(posts),1)
                self.assertEqual(posts[0]['content_type'],'观点')


if __name__=='__main__': unittest.main()
