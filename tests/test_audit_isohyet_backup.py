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
            self.assertEqual(report["backup_sha256"], before)
            self.assertEqual(len(report["entries"]), 3)
            self.assertEqual(report["entries"][0]["isohyet_reference_count"], 0)
            self.assertNotIn("SECRET_DO_NOT_REPORT", json.dumps(report))
            self.assertFalse((Path(tmp) / "online").exists())

    def test_backup_hash_changes_with_archive_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.zip"
            second = Path(tmp) / "second.zip"
            self.make_zip(first, {"online/station_match_v39.js": "v39-A"})
            self.make_zip(second, {"online/station_match_v39.js": "v39-B"})
            a = audit(first)
            b = audit(second)
            self.assertEqual(a["backup_sha256"], sha256(first.read_bytes()))
            self.assertEqual(b["backup_sha256"], sha256(second.read_bytes()))
            self.assertNotEqual(a["backup_sha256"], b["backup_sha256"])
            self.assertFalse(a["deploy_allowed"])
            self.assertFalse(b["deploy_allowed"])

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
                "online\\station_isohyet_v26.html": "map UI",
                "online\\station_match_v39.js": "matcher",
            })
            report = audit(backup)
            self.assertEqual(len(report["entries"]), 2)
            self.assertFalse(any("Missing from supplied archive" in w for w in report["warnings"]))
            self.assertFalse(report["deploy_allowed"])

    def test_conflicting_asset_copies_require_manual_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "multi-root.zip"
            self.make_zip(backup, {
                "public_html/online/station_match_v39.js": "new resolver",
                "old_backup/online/station_match_v39.js": "old resolver",
                "public_html/online/station_isohyet_v26.html": "tool",
            })
            report = audit(backup)
            self.assertEqual(len(report["entries"]), 3)
            self.assertTrue(any("Ambiguous backup candidates for station_match_v39.js: 2 copies" in w
                                for w in report["warnings"]))
            self.assertFalse(any("Missing from supplied archive" in w for w in report["warnings"]))
            self.assertFalse(report["deploy_allowed"])

    def test_single_asset_copy_does_not_trigger_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "single-root.zip"
            self.make_zip(backup, {
                "public_html/online/station_match_v39.js": "resolver",
                "public_html/online/station_isohyet_v26.html": "tool",
            })
            report = audit(backup)
            self.assertFalse(any("Ambiguous backup candidates" in w for w in report["warnings"]))

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

    def test_reject_unsafe_directory_entries_even_if_no_files_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "bad-dir.zip"
            with zipfile.ZipFile(backup, "w") as z:
                z.writestr("online/../", "")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                inspect_zip(backup)

    def test_accept_normal_directory_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "normal-dir.zip"
            with zipfile.ZipFile(backup, "w") as z:
                z.writestr("online/", "")
                z.writestr("online/station_match_v39.js", "resolver")
            self.assertEqual(len(inspect_zip(backup)), 1)

    def test_reject_repeated_directory_trailing_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "double-slash-dir.zip"
            with zipfile.ZipFile(backup, "w") as z:
                z.writestr("online//", "")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                inspect_zip(backup)

    def test_reject_compression_bomb_relevant_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "bomb.zip"
            with zipfile.ZipFile(backup, "w", compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("index.html", "X" * 1000000)
            with self.assertRaisesRegex(ValueError, "compression ratio"):
                inspect_zip(backup)

    def test_reject_ambiguous_dot_empty_and_control_segments(self):
        for bad in ("", ".", "./index.html", "online//station_match_v39.js",
                    "online/./station_match_v39.js", "online/../index.html",
                    "online\\\\.\\\\station_match_v39.js",
                    "online/sta" + chr(0) + "tion_match_v39.js", "online/" + chr(1) + "index.html"):
            with self.subTest(path=repr(bad)):
                self.assertFalse(safe_name(bad))

    def test_reject_alias_path_before_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "ambiguous.zip"
            self.make_zip(backup, {
                "online/station_match_v39.js": "canonical",
                "online/./station_match_v39.js": "ambiguous",
            })
            with self.assertRaises(ValueError):
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
