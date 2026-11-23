"""Read-only Stage22 host preflight regression checks (no cPanel access)."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.metstat_stage29_host_preflight import scan, STAGE22, PINNED


class TestStage29Preflight(unittest.TestCase):
    def test_missing_required_files_fail_closed(self):
        with TemporaryDirectory() as tmp:
            report = scan(Path(tmp))
            self.assertFalse(report["ok"])
            self.assertFalse(report["active_cpanel_verified"])
            self.assertEqual(report["checked"], 0)
            self.assertTrue(any(x["path"] == "index.html" and x["problem"] == "missing"
                                for x in report["issues"]))

    def test_unexpected_active_index_fails_without_writing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("unknown active version", encoding="utf-8")
            before = hashlib.sha256((root / "index.html").read_bytes()).hexdigest()
            report = scan(root)
            after = hashlib.sha256((root / "index.html").read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertFalse(report["ok"])
            self.assertTrue(any(x["path"] == "index.html" and
                                x["problem"] == "unexpected-version" for x in report["issues"]))

    def test_required_scientific_engine_missing_is_blocker(self):
        with TemporaryDirectory() as tmp:
            report = scan(Path(tmp))
            self.assertTrue(any(x["path"] == "online/station_isohyet_v26.html"
                                and x["problem"] == "missing" for x in report["issues"]))


if __name__ == "__main__":
    unittest.main()
