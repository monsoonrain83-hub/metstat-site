"""Source-pinned Stage40 deterministic Atlas patch; no live cPanel artifacts needed."""
import re
import unittest

from tools.r5_stage40_atlas_patch import (
    BEFORE, AFTER, OLD_REVEAL, NEW_REVEAL,
    OLD_COLLAPSE, NEW_COLLAPSE, apply, sha,
)


def fixture():
    scripts=[]
    for i in range(19):
        if i==11:
            body='function caAtlas() { ' + OLD_REVEAL + ' }catch(e){} }\n' + (
                OLD_COLLAPSE + ' }')
        else:
            body=f'const atlas_fixture_{i}={i};'
        scripts.append('<script>'+body+'</script>')
    source=('<html><head><style id="ms9-desktop-r5-system">'
            + BEFORE + '</style></head><body>'
            + ''.join(scripts) + '</body></html>')
    return source.encode('utf-8')


class Stage40SourcePatch(unittest.TestCase):
    def setUp(self):
        self.src=fixture()
        self.src_sha=sha(self.src)

    def apply(self, blob=None, target_sha=None):
        data=self.src if blob is None else blob
        return apply(data,source_sha=self.src_sha,target_sha=target_sha)

    def test_exact_source_owner_only(self):
        result=self.apply()
        before=self.src.decode()
        after=result.decode()
        self.assertIn(AFTER,after)
        self.assertNotIn(BEFORE,after)
        self.assertIn(NEW_REVEAL,after)
        self.assertIn(NEW_COLLAPSE,after)
        self.assertEqual(before.count('!important'),after.count('!important'))
        self.assertEqual(len(re.findall(r'<script',after)),19)
        old_sections=re.findall(r'<script>(.*?)</script>',before,re.S)
        new_sections=re.findall(r'<script>(.*?)</script>',after,re.S)
        self.assertEqual([i for i,(a,b) in enumerate(zip(old_sections,new_sections)) if a!=b],[11])

    def test_unknown_source_sha_rejected(self):
        with self.assertRaises(ValueError):
            self.apply(self.src+b'external update')

    def test_reapplication_rejected(self):
        with self.assertRaises(ValueError):
            self.apply(self.apply())

    def test_wrong_expected_target_rejected(self):
        with self.assertRaises(ValueError):
            self.apply(target_sha='0'*64)

    def test_duplicate_atlas_css_anchor_rejected(self):
        duplicate=self.src.replace(b'</style>',BEFORE.encode()+b'</style>')
        with self.assertRaises(ValueError):
            apply(duplicate,source_sha=sha(duplicate),target_sha=None)

    def test_do_not_accept_missing_collapsible_owner(self):
        corrupt=self.src.replace(OLD_COLLAPSE.encode(),b'function caCollapse(){return;')
        with self.assertRaises(ValueError):
            apply(corrupt,source_sha=sha(corrupt),target_sha=None)


if __name__=='__main__':
    unittest.main()
