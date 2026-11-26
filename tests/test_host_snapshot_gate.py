import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import hashlib
from scripts import check_host_snapshot as gate

class HostSnapshotGateTests(unittest.TestCase):
    def test_match_drift_and_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "online").mkdir()
            (root / "index.html").write_bytes(b"index")
            (root / "online/nwp_upload.php").write_bytes(b"uploader")
            expected = {"index.html": hashlib.sha256(b"index").hexdigest(),
                        "online/nwp_upload.php": hashlib.sha256(b"uploader").hexdigest()}
            with patch.object(gate, "EXPECTED", expected):
                self.assertEqual([r["status"] for r in gate.check(root)], ["match", "match"])
                (root / "index.html").write_bytes(b"old")
                (root / "online/nwp_upload.php").unlink()
                self.assertEqual([r["status"] for r in gate.check(root)], ["drift", "missing-or-unsafe"])

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "host"
            root.mkdir()
            other = Path(td) / "outside"
            other.write_bytes(b"not a host file")
            (root / "index.html").symlink_to(other)
            with patch.object(gate, "EXPECTED", {"index.html": hashlib.sha256(other.read_bytes()).hexdigest()}):
                self.assertEqual(gate.check(root)[0]["status"], "missing-or-unsafe")

    def test_release_pins_distinguish_versions_and_pair_core(self):
        v87 = gate.release_expected("V87")
        v88 = gate.release_expected("V88")
        self.assertNotEqual(v87["index.html"], v88["index.html"])
        for expected in (v87, v88):
            core = next(p for p in expected if p.startswith("assets/"))
            self.assertEqual(core, f"assets/ms_r5_perf_core_{expected[core][:16]}.js")
            self.assertEqual(expected["online/nwp_upload.php"], gate.EXPECTED["online/nwp_upload.php"])

    def test_wrong_release_or_missing_core_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "assets").mkdir()
            (root / "index.html").write_bytes(b"old")
            expected = {"index.html": hashlib.sha256(b"new").hexdigest(),
                        "assets/core.js": hashlib.sha256(b"new core").hexdigest()}
            self.assertEqual([r["status"] for r in gate.check(root, expected)],
                             ["drift", "missing-or-unsafe"])

    def test_parent_symlink_within_root_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "real").mkdir()
            (root / "real/core.js").write_bytes(b"core")
            (root / "assets").symlink_to(root / "real", target_is_directory=True)
            self.assertEqual(gate.check(root, {"assets/core.js": hashlib.sha256(b"core").hexdigest()})[0]["status"],
                             "missing-or-unsafe")

if __name__ == "__main__":
    unittest.main()
