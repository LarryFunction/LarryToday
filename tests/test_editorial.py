import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime,timezone
from scripts.editorial import window,partition,events,diverse,classify
from scripts.editions import save

class EditionTests(unittest.TestCase):
    def test_before_and_after_cutoff(self):
        self.assertEqual(window(datetime(2026,10,18,22,59,tzinfo=timezone.utc))['date'],'2026-10-18')
        self.assertEqual(window(datetime(2026,10,18,23,0,tzinfo=timezone.utc))['date'],'2026-10-19')
        with self.assertRaises(ValueError): window(datetime(2026,10,18,tzinfo=timezone.utc),'2026-10-20')

    def row(self,id,date,source='bbc'):
        return {'id':id,'title':'News','url':'https://example.com/'+id,'source_id':source,'category':'国际政治','published_at':date}

    def test_window_boundaries_and_unknown(self):
        bounds=window(datetime(2026,10,19,tzinfo=timezone.utc))
        rows=[self.row('a',bounds['start']),self.row('b',bounds['end']),self.row('c',None),self.row('d','2026-10-17T20:00:00Z')]
        main,background,excluded=partition(rows,bounds)
        self.assertEqual([r['id'] for r in main],['a'])
        self.assertEqual([r['id'] for r in background],['d'])
        self.assertEqual(excluded['unknown_date'],1)

    def test_no_transitive_merge_or_same_family(self):
        rows=[self.row('a','2026-10-18T20:00:00Z'),self.row('b','2026-10-18T21:00:00Z','guardian'),self.row('c','2026-10-18T21:00:00Z','npr')]
        groups=[{'article_ids':['a','b'],'title_zh':'AB'},{'article_ids':['b','c'],'title_zh':'BC'}]
        result=events(rows,groups)
        self.assertEqual(len(result),2)
        rows[1]['publisher_family']='bbc'
        self.assertEqual(len(events(rows,groups[:1])),3)

    def test_initial_bytes_immutable_and_revision_requires_note(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            data=Path(temp);base={'date':'2026-10-18','articles':[]}
            self.assertEqual(save(data,dict(base)),1)
            path=data/'editions/2026-10-18.json';before=path.read_bytes()
            with self.assertRaises(ValueError): save(data,dict(base))
            self.assertEqual(save(data,dict(base,articles=[{'title':'Correction'}]),'更正标题'),2)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(json.loads((data/'latest.json').read_text(encoding='utf-8'))['revision'],2)
            self.assertEqual(len(json.loads((data/'revisions/2026-10-18/index.json').read_text(encoding='utf-8'))),2)

    def test_diverse_selection(self):
        rows=[self.row(str(i),'2026-10-18T20:00:00Z','guardian') for i in range(8)]+[self.row('x','2026-10-18T20:00:00Z','cna')]
        self.assertIn('cna',[r['source_id'] for r in diverse(rows,3)])

    def test_publisher_section_overrides_broad_keyword(self):
        row=self.row('a','2026-10-18T20:00:00Z')
        row.update(url='https://example.com/deportes/story',title='Club stock market deal')
        self.assertEqual(classify(row)['category'],'社会与文化')
        row.update(url='https://example.com/world/story',title='Título',title_zh='人工智能大学考试')
        self.assertEqual(classify(row)['category'],'科技与 AI')

    def test_social_snapshot_excludes_future_and_remains_immutable(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            data=Path(temp);bounds=window(datetime(2026,10,19,tzinfo=timezone.utc))
            posts=[self.row('a',bounds['start']),self.row('b',bounds['end'])]
            (data/'social-posts.json').write_text(json.dumps(posts),encoding='utf-8')
            save(data,{'date':bounds['date'],'window':bounds,'articles':[]})
            (data/'social-posts.json').write_text('[]',encoding='utf-8')
            snapshot=json.loads((data/'latest.json').read_text(encoding='utf-8'))
            self.assertEqual([p['id'] for p in snapshot['social_posts']],['a'])

if __name__=='__main__': unittest.main()
