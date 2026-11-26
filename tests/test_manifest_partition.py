import copy
import unittest
from manifest_partition import partition, reconstruct, report

class ManifestPartitionTests(unittest.TestCase):
    def setUp(self):
        self.m = {'models': {'a': {'run':'2026112600'}, 'b': {'run':'2026112518'}}, 'items': [{'m':'b','v':'2026112600','w':1}, {'m':'a','v':'2026112700','x':'webp'}, {'m':'b','v':'2026112606'}], 'items_prev':[{'m':'a','v':'2026112500'}], 'unknown_metadata': {'fa':'ایران'}}
    def test_roundtrip_order_and_optional_fields(self):
        c,s=partition(self.m)
        self.assertEqual(reconstruct(c,s),self.m)
    def test_empty_previous(self):
        self.m['items_prev']=[]
        c,s=partition(self.m)
        self.assertEqual(reconstruct(c,s),self.m)
    def test_missing_shard(self):
        c,s=partition(self.m);s.pop(('items','a'))
        with self.assertRaises(ValueError): reconstruct(c,s)
    def test_corruption(self):
        c,s=partition(self.m);s=copy.deepcopy(s);s[('items','a')][0][1]['v']='bad'
        with self.assertRaises(ValueError): reconstruct(c,s)
    def test_wrong_model(self):
        self.m['items'][0]['m']='unknown'
        with self.assertRaises(ValueError): partition(self.m)
    def test_duplicate_spec(self):
        c,s=partition(self.m);c['shards'].append(c['shards'][0])
        with self.assertRaises(ValueError): reconstruct(c,s)
    def test_metadata_change(self):
        c,s=partition(self.m);c['metadata']['unknown_metadata']={'fa':'changed'}
        with self.assertRaises(ValueError): reconstruct(c,s)
    def test_preserve_duplicate_rows(self):
        self.m['items'].append(self.m['items'][0].copy())
        c,s=partition(self.m);self.assertEqual(reconstruct(c,s),self.m)
if __name__=='__main__': unittest.main()
