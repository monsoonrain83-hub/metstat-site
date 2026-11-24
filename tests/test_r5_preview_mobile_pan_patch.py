"""Pinned, minimal R5 mobile horizontal-pan fix tests."""
from hashlib import sha256
import unittest
from tools.r5_preview_mobile_pan_patch import ORIGINAL, REVISED, patch


class MobilePanPatch(unittest.TestCase):
    def test_one_exact_css_block_change_no_js_touch(self):
        source = b'<script>const state="unchanged"</script>\n' + ORIGINAL + b'\n<data>BASE64_PRESERVED</data>'
        patched = patch(source, sha256(source).hexdigest())
        self.assertEqual(patched, source.replace(ORIGINAL, REVISED, 1))
        self.assertIn(b'const state="unchanged"', patched)
        self.assertIn(b'BASE64_PRESERVED', patched)
        self.assertNotIn(b'!important', patched)

    def test_rejects_unpinned_new_version(self):
        with self.assertRaisesRegex(ValueError, "source drift"):
            patch(ORIGINAL)

    def test_rejects_duplicate_rule(self):
        source = ORIGINAL + ORIGINAL
        with self.assertRaisesRegex(ValueError, "absent or duplicated"):
            patch(source, sha256(source).hexdigest())

    def test_rejects_second_application(self):
        with self.assertRaisesRegex(ValueError, "absent or duplicated"):
            patch(REVISED, sha256(REVISED).hexdigest())


if __name__ == '__main__':
    unittest.main()
