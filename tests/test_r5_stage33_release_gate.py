"""Offline release preflight regression; never accesses cPanel."""
from hashlib import sha256
from io import BytesIO
import unittest
from zipfile import ZipFile

from tools.r5_stage33_release_gate import checks


def digest(data):
    return sha256(data).hexdigest()


def archive(files):
    bio = BytesIO()
    with ZipFile(bio, "w") as z:
        for name, data in files:
            z.writestr(name, data)
    return bio.getvalue()


BASE = b"<html><div id=\"onEmpty\"></div><div id=\"onViewer\" hidden></div>" + b"".join(
    b"<script>const n%d=%d;</script>" % (i, i) for i in range(14)
) + b"</html>"
CANDIDATE = BASE.replace(b'id="onEmpty"', b'id="onEmpty" class="ms33-r5-empty"')
ZIP = archive([("index.html", CANDIDATE)])


def audit(base=BASE, candidate=CANDIDATE, package=ZIP, baseline=BASE):
    return checks(base, candidate, package,
                  original_hash="0"*64, stage32_hash=digest(baseline),
                  stage33_hash=digest(CANDIDATE))


class Stage33Gate(unittest.TestCase):
    def test_valid_incremental_candidate(self):
        r = audit()
        self.assertTrue(r["passed"], r)

    def test_rejects_stale_baseline(self):
        self.assertFalse(audit(base=BASE+b"x")["checks"]["baseline_pinned"])

    def test_rejects_modified_inline_code(self):
        changed = CANDIDATE.replace(b"const n5=5;", b"const n5=6;")
        self.assertFalse(audit(candidate=changed)["checks"]["scripts_unchanged"])

    def test_rejects_duplicate_dom_id(self):
        changed = CANDIDATE.replace(b"</html>", b'<b id="onViewer"></b></html>')
        self.assertFalse(audit(candidate=changed)["checks"]["no_new_duplicate_ids"])

    def test_rejects_new_important(self):
        self.assertFalse(audit(candidate=CANDIDATE+b"!important")["checks"]["no_added_important_rules"])

    def test_rejects_unrecognized_zip_entry(self):
        bad = archive([("index.html", CANDIDATE), ("install.php", b"danger")])
        self.assertFalse(audit(package=bad)["checks"]["zip_safe_paths"])

    def test_rejects_duplicate_index_zip(self):
        bad = archive([("index.html", CANDIDATE), ("index.html", CANDIDATE)])
        self.assertFalse(audit(package=bad)["checks"]["zip_unique"])

    def test_rejects_changed_index_in_zip(self):
        bad = archive([("index.html", CANDIDATE+b"changed")])
        self.assertFalse(audit(package=bad)["checks"]["zip_index_sha"])

    def test_rejects_missing_marker(self):
        bad = CANDIDATE.replace(b"ms33-r5-empty", b"plain")
        self.assertFalse(audit(candidate=bad)["checks"]["single_status_shell"])


if __name__ == "__main__":
    unittest.main()
