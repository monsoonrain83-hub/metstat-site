"""Stage41 deterministic patch tests. No cPanel access or user data needed."""
import unittest
from tools.r5_stage41_native_panel_patch import (
    ATLAS_OLD, ATLAS_NEW, SF_OLD, SF_NEW, CSS_NEW, patch, sha, parts,
)


def fixture():
    scripts=[]
    for i in range(19):
        body=ATLAS_OLD+"\n"+SF_OLD if i==11 else "const fixture_"+str(i)+"="+str(i)+";"
        scripts.append("<script>"+body+"</script>")
    styles=[]
    for i in range(7):
        if i==5:
            styles.append('<style id="ms9-desktop-r5-system">.existing{color:#333}</style>')
        else:
            styles.append("<style>.other"+str(i)+"{display:block}</style>")
    return ("<!doctype html><html><head>"+"".join(styles)+
            "</head><body><div id=\"caAside\"></div><div id=\"caCards\"></div>"+
            "<div id=\"caApp\"></div><div id=\"sfMain\"></div>"+
            "".join(scripts)+"</body></html>").encode()


class Stage41SourcePatch(unittest.TestCase):
    def setUp(self):
        self.index=fixture()
        self.expected_source_sha=sha(self.index)

    def candidate(self, data=None, target_sha=None):
        return patch(self.index if data is None else data,
                     source_sha=self.expected_source_sha,target_sha=target_sha)

    def test_only_approved_r5_owners_change(self):
        old=self.index.decode()
        new=self.candidate().decode()
        changes=lambda tag:[i for i,(a,b) in enumerate(zip(parts(old,tag),parts(new,tag))) if a!=b]
        self.assertEqual(changes("script"),[11])
        self.assertEqual(changes("style"),[5])
        self.assertIn(ATLAS_NEW,new)
        self.assertIn(SF_NEW,new)
        self.assertIn(CSS_NEW,new)
        self.assertEqual(old.count('!important'),new.count('!important'))

    def test_source_drift_refused(self):
        with self.assertRaises(ValueError):
            self.candidate(self.index+b"unexpected admin update")

    def test_double_application_refused(self):
        with self.assertRaises(ValueError):
            self.candidate(self.candidate())

    def test_wrong_target_pin_refused(self):
        with self.assertRaises(ValueError):
            self.candidate(target_sha="0"*64)

    def test_duplicate_native_owner_refused(self):
        modified=self.index.replace(b'</body>',ATLAS_OLD.encode()+b'</body>')
        with self.assertRaises(ValueError):
            patch(modified,source_sha=sha(modified),target_sha=None)

    def test_missing_native_seasonal_owner_refused(self):
        modified=self.index.replace(SF_OLD.encode(),b'/* removed */')
        with self.assertRaises(ValueError):
            patch(modified,source_sha=sha(modified),target_sha=None)


if __name__=='__main__':
    unittest.main()
