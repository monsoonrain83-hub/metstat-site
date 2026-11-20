"""Release verification is intentionally offline, strict and read-only."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.metstat_release_preflight import validate


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "assets").mkdir()
        self.base_version = {
            "build": "same-science", "base": "same-data", "database": "private-v45",
            "ui_build": "r120"
        }
        self.release_version = dict(self.base_version, ui_build="r121")
        self.before = json.dumps(self.base_version, sort_keys=True).encode()
        self.after = json.dumps(self.release_version, sort_keys=True).encode()
        self.manifest = {
            "changed_upload_files": ["index.html", "version.json", "assets/new.css"],
            "full_release_subset": ["index.html", "version.json", "assets/new.css"],
            "ui_build_before": "r120",
            "ui_build_after": "r121",
            "preserved_contract": {
                "build": "same-science", "base": "same-data", "database": "private-v45"
            },
            "file_hashes": {
                "index.html": {"before_sha256": digest(b"old"), "after_sha256": digest(b"new")},
                "version.json": {"before_sha256": digest(self.before), "after_sha256": digest(self.after)},
                "assets/new.css": {"before_sha256": None, "after_sha256": digest(b"css")}
            }
        }
        (self.root / "index.html").write_bytes(b"old")
        (self.root / "version.json").write_bytes(self.before)
        self.manifest_file = self.root / "manifest.json"
        self.manifest_file.write_text(json.dumps(self.manifest), encoding="utf-8")

    def run_gate(self, phase):
        return validate(self.root, self.manifest_file, phase)

    def test_base_and_release_hashes(self):
        self.assertEqual(self.run_gate("base")[1], [])
        (self.root / "index.html").write_bytes(b"new")
        (self.root / "version.json").write_bytes(self.after)
        (self.root / "assets/new.css").write_bytes(b"css")
        self.assertEqual(self.run_gate("release")[1], [])

    def test_mismatch_blocks(self):
        (self.root / "index.html").write_bytes(b"accidental overwrite")
        self.assertTrue(any("SHA256 mismatch" in s for s in self.run_gate("base")[1]))

    def test_preexisting_new_asset_blocks(self):
        (self.root / "assets/new.css").write_bytes(b"not expected")
        self.assertTrue(any("Unexpected pre-existing" in s for s in self.run_gate("base")[1]))

    def test_changed_backend_contract_blocks(self):
        bad = dict(self.base_version, database="other-private")
        (self.root / "version.json").write_text(json.dumps(bad), encoding="utf-8")
        self.assertTrue(any("Preserved contract" in s for s in self.run_gate("base")[1]))

    def test_path_traversal_blocks(self):
        self.manifest["changed_upload_files"].append("../escape.html")
        self.manifest["file_hashes"]["../escape.html"] = {"before_sha256": digest(b""), "after_sha256": digest(b"")}
        self.manifest_file.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.assertTrue(any("Path escapes" in s for s in self.run_gate("base")[1]))


if __name__ == "__main__":
    unittest.main()
