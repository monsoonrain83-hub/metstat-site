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


    def test_symlink_inside_root_is_rejected_even_when_target_hash_matches(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "saved_index.html"
            target.write_text("original", encoding="utf-8")
            (root / "index.html").symlink_to(target)
            report = scan(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any(x["path"] == "index.html" and
                                x["problem"] == "symlink-not-allowed" for x in report["issues"]))
            self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_dangling_symlink_is_rejected_not_reported_as_optional_missing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").mkdir()
            (root / "assets/metstat_map_ui_r201.css").symlink_to(root / "does-not-exist")
            report = scan(root)
            self.assertTrue(any(x["path"] == "assets/metstat_map_ui_r201.css" and
                                x["problem"] == "symlink-not-allowed" for x in report["issues"]))

    def test_symlinked_parent_directory_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "store").mkdir()
            (root / "online").symlink_to(root / "store", target_is_directory=True)
            report = scan(root)
            self.assertTrue(any(x["path"] == "online/station_isohyet_v26.html" and
                                x["problem"] == "symlink-not-allowed" for x in report["issues"]))


if __name__ == "__main__":
    unittest.main()
