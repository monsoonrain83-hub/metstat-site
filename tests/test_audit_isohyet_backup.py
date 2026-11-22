import io
import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from tools.audit_isohyet_backup import audit, inspect_zip, safe_name, sha256


class BackupAuditTests(unittest.TestCase):
    def make_zip(self, path, entries):
        with zipfile.ZipFile(path, "w") as z:
            for name, body in entries.items():
                z.writestr(name, body)

    def test_missing_nav_and_assets_reported_without_modifying_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "backup.zip"
            self.make_zip(backup, {
                "index.html": "<html>forecast</html>",
                "online/station_isohyet_v26.html": "real station tool",
                "online/station_match_v39.js": "resolver",
                "admin/private/config.json": "SECRET_DO_NOT_REPORT",
            })
            before = sha256(backup.read_bytes())
            report = audit(backup)
            self.assertFalse(report["deploy_allowed"])
            self.assertFalse(report["live_verified"])
            self.assertEqual(sha256(backup.read_bytes()), before)
            self.assertEqual(len(report["entries"]), 3)
            self.assertEqual(report["entries"][0]["isohyet_reference_count"], 0)
            self.assertNotIn("SECRET_DO_NOT_REPORT", json.dumps(report))
            self.assertFalse((Path(tmp) / "online").exists())

    def test_missing_matcher_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "b.zip"
            self.make_zip(backup, {"index.html": "همبارش"})
            report = audit(backup)
            self.assertTrue(any("station_match_v39.js" in x for x in report["warnings"]))
            self.assertEqual(report["entries"][0]["isohyet_reference_count"], 1)

    def test_active_index_is_not_live_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "b.zip"
            active = Path(tmp) / "active.html"
            active.write_text("isohyet", encoding="utf-8")
            self.make_zip(backup, {"index.html": "no nav"})
            report = audit(backup, active)
            self.assertEqual(report["active_index"]["isohyet_reference_count"], 1)
            self.assertFalse(report["deploy_allowed"])
            self.assertFalse(report["live_verified"])

    def test_reject_duplicate_casefolded_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "duplicate.zip"
            self.make_zip(backup, {"index.html": "A", "INDEX.HTML": "B"})
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                inspect_zip(backup)

    def test_reject_duplicate_mixed_windows_and_posix_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "duplicate-separator.zip"
            self.make_zip(backup, {
                "online/station_match_v39.js": "version A",
                "online\\station_match_v39.js": "version B",
            })
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                inspect_zip(backup)

    def test_windows_separated_assets_are_inventoried_without_false_missing_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "windows.zip"
            self.make_zip(backup, {
                "online\\\\station_isohyet_v26.html": "map UI",
                "online\\\\station_match_v39.js": "matcher",
            })
            report = audit(backup)
            self.assertEqual(len(report["entries"]), 2)
            self.assertFalse(any("Missing from supplied archive" in w for w in report["warnings"]))
            self.assertFalse(report["deploy_allowed"])

    def test_reject_single_windows_separator_traversal(self):
        self.assertFalse(safe_name("online\\..\\..\\index.html"))
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "windows-traversal.zip"
            self.make_zip(backup, {"online\\..\\..\\index.html": "unsafe"})
            with self.assertRaises(ValueError):
                inspect_zip(backup)

    def test_reject_symlink_even_when_name_is_irrelevant(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "symlink.zip"
            with zipfile.ZipFile(backup, "w") as z:
                link = zipfile.ZipInfo("hidden-link")
                link.create_system = 3
                link.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(link, "target")
            with self.assertRaisesRegex(ValueError, "Symbolic"):
                inspect_zip(backup)

    def test_reject_compression_bomb_relevant_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "bomb.zip"
            with zipfile.ZipFile(backup, "w", compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("index.html", "X" * 1000000)
            with self.assertRaisesRegex(ValueError, "compression ratio"):
                inspect_zip(backup)

    def test_reject_zip_slip_and_absolute_members(self):
        for bad in ("../index.html", "/index.html", "C:/index.html"):
            self.assertFalse(safe_name(bad))
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "b.zip"
            self.make_zip(backup, {"../index.html": "x"})
            with self.assertRaises(ValueError):
                inspect_zip(backup)


if __name__ == "__main__":
    unittest.main()
