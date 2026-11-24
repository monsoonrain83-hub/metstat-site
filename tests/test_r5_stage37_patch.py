"""Stage37 deterministic native JS patch tests; no live host credentials needed."""
from hashlib import sha256
import unittest

from tools.r5_stage37_patch import PATCHES, apply, sha, scripts


def fixture() -> bytes:
    # 12 inline scripts; both exact patch anchors are owned by script #11.
    standard = "".join(f"<script>const v{i}={i};</script>" for i in range(11))
    owner = "<script>function nvImg() {\n" + PATCHES[0][0] + "\n}\nfunction nvResolve() {\n" + PATCHES[1][0] + "\n}\n</script>"
    return (
        '<!doctype html><html><head><style>body { color: red !important; }</style></head>'
        '<body><div id="onAside"></div><div id="onEmpty"></div>'
        '<div id="onViewer" hidden></div>' + standard + owner + '</body></html>'
    ).encode()


class Stage37PatchTest(unittest.TestCase):
    def setUp(self):
        self.source = fixture()
        self.hash = sha(self.source)

    def patch(self, source=None):
        return apply(self.source if source is None else source,
                     source_sha=self.hash, target_sha=None)

    def test_patch_changes_only_expected_owner(self):
        candidate = self.patch()
        old, new = scripts(self.source.decode()), scripts(candidate.decode())
        self.assertEqual([i for i, (a, b) in enumerate(zip(old, new)) if a != b], [11])
        self.assertIn("NV.cache.get(url)===p", candidate.decode())
        self.assertIn('pending.hidden=true', candidate.decode())

    def test_unknown_hash_rejected(self):
        with self.assertRaises(ValueError):
            apply(self.source + b' ', source_sha=self.hash, target_sha=None)

    def test_second_application_rejected(self):
        with self.assertRaises(ValueError):
            self.patch(self.patch())

    def test_duplicate_anchor_rejected(self):
        extra = self.source.replace(b"</body>", PATCHES[0][0].encode() + b"</body>")
        with self.assertRaises(ValueError):
            apply(extra, source_sha=sha(extra), target_sha=None)

    def test_not_same_as_release_target(self):
        with self.assertRaises(ValueError):
            apply(self.source, source_sha=self.hash, target_sha="f" * 64)

    def test_refuses_missing_protected_dom(self):
        modified = self.source.replace(b'id="onAside"', b'id="removed"')
        with self.assertRaises(ValueError):
            apply(modified, source_sha=sha(modified), target_sha=None)


if __name__ == "__main__":
    unittest.main()
