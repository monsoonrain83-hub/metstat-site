import importlib.util
import tempfile
from pathlib import Path
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("guard", Path(__file__).resolve().parents[1] / "scripts/check_rainfall_api_contract.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class TestRainfallApiContract(unittest.TestCase):
    def test_v75_regression(self):
        self.assertTrue(g.check_contract("'version'=>'61-candidate'\n'version'=>'75-catalog'", "if(x.version!=='61-candidate')"))
    def test_v76_compatible(self):
        self.assertEqual(g.check_contract("'version'=>'61-candidate'\n'version'=>'61-candidate'", "if(!['61-candidate','75-catalog'].includes(x.version))"), [])
    def test_legacy_client(self):
        self.assertEqual(g.check_contract("'version'=>'61-candidate'", "if(x.version!=='61-candidate')"), [])
    def test_unknown_declaration(self):
        self.assertTrue(g.check_contract("", ""))
    def test_release_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "release.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr(g.API, "'version'=>'61-candidate'")
                z.writestr(g.CLIENT, "if(!['61-candidate','75-catalog'].includes(x.version))")
            self.assertEqual(g.check_release(p), [])
            with zipfile.ZipFile(p, "w") as z:
                z.writestr(g.API, "'version'=>'61-candidate'")
            self.assertTrue(g.check_release(p))

if __name__ == "__main__":
    unittest.main()
