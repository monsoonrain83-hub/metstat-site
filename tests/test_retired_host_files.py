import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('guard',Path(__file__).resolve().parents[1]/'scripts/check_retired_host_files.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class TestRetiredHostFiles(unittest.TestCase):
    def test_each_confirmed_removed_file_rejected(self):
        self.assertEqual(len(g.RETIRED),15)
        for p in g.RETIRED:
            self.assertTrue(g.check_names([p]))
            self.assertTrue(g.check_names(['public_html/'+p]))
            self.assertTrue(g.check_names(['release/'+p.upper()]))
    def test_active_files_allowed(self):
        self.assertEqual(g.check_names(['index.html','online/station_isohyet_unified_v66.html','assets/ms_r5_perf_core_5bf9868a04910eee.js','online/rain_station_lookup_unified_v61.php','online/metstat_native_pages.php']),[])
    def test_unsafe_names(self):
        for p in ('../index.html','/index.html','x/../../index.html','x\\index.html','C:/index.html'):
            self.assertTrue(g.check_names([p]))
    def test_real_zip_and_directory(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            z=p/'candidate.zip'
            with zipfile.ZipFile(z,'w') as f:
                f.writestr('public html/online/api.zip','')
            self.assertTrue(g.check(z))
            root=p/'release'
            root.mkdir()
            (root/'index.html').write_text('ok')
            self.assertEqual(g.check(root),[])
            (root/'metstat_geo_r203_install.php').write_text('old')
            self.assertTrue(g.check(root))
if __name__=='__main__':
    unittest.main()
