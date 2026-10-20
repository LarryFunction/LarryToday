import unittest
from scripts.collect import expected_empty
class FeedStatusTests(unittest.TestCase):
    def test_empty_arxiv_is_not_outage(self):
        xml=b'<rss><channel><title>cs.AI</title></channel></rss>'
        self.assertTrue(expected_empty(xml,{'source_id':'arxiv'}))
        self.assertFalse(expected_empty(xml,{'source_id':'bbc'}))
        self.assertFalse(expected_empty(b'<html/>',{'source_id':'arxiv'}))
        self.assertFalse(expected_empty(b'<rss><channel><item/></channel></rss>',{'source_id':'arxiv'}))
