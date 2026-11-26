import tempfile, unittest, zipfile, stat
from pathlib import Path
from verify_frontend_release import verify, digest
class Release(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'candidate.zip'
        self.old=b'const x=1;';self.new=b'const x=2;'
        self.oldname='assets/ms_r5_perf_core_'+digest(self.old)[:16]+'.js'
        self.name='assets/ms_r5_perf_core_'+digest(self.new)[:16]+'.js'
        self.html=lambda n:('<html><script src="/'+n+'"></script></html>').encode()
    def make(self,extras=(),name=None,body=None,index=None,link=False):
        n=name or self.name
        with zipfile.ZipFile(self.path,'w') as z:
            z.writestr('index.html',self.html(n) if index is None else index)
            if link:
                x=zipfile.ZipInfo(n);x.create_system=3;x.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(x,body or self.new)
            else:z.writestr(n,self.new if body is None else body)
            for k,v in extras:z.writestr(k,v)
    def check(self):return verify(self.path,self.html(self.oldname),self.old,self.oldname)
    def test_valid(self):self.make();self.assertEqual(self.check()['core_sha256'],digest(self.new))
    def test_extra(self):self.make(extras=[('admin/index.php',b'x')]);self.assertRaises(ValueError,self.check)
    def test_traversal(self):self.make(name='../'+self.name);self.assertRaises(ValueError,self.check)
    def test_hash(self):self.make(body=b'wrong');self.assertRaises(ValueError,self.check)
    def test_html_changes(self):self.make(index=self.html(self.name)+b'changed');self.assertRaises(ValueError,self.check)
    def test_double_reference(self):self.make(index=self.html(self.name)+self.html(self.name));self.assertRaises(ValueError,self.check)
    def test_symlink(self):self.make(link=True);self.assertRaises(ValueError,self.check)
    def test_no_change(self):self.make(name=self.oldname,body=self.old);self.assertRaises(ValueError,self.check)
if __name__=='__main__':unittest.main()
