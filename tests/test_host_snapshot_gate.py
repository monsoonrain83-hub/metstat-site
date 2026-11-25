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

if __name__ == "__main__":
    unittest.main()
