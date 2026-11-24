"""Stage40 release gate: keep both genuine climate atlas settings panels accessible."""
import unittest
from tools.r5_stage40_host_gate import check, sha, SOURCE_SHA256, TARGET_SHA256
from test_r5_stage39_host_gate import fixture as parent_fixture, zipfile as make_zip

PATCH_CSS = (
    "html.ms9-active #caApp.wrap:not([hidden]){display:grid;"
    "grid-template-columns:var(--ms9-sidebar-width,328px) minmax(0,1fr);}"
    "html.ms9-active #caApp>aside#caAside{grid-row:1}"
    "html.ms9-active #caApp>aside#caAside2{grid-row:2}"
    "html.ms9-active #caApp>main{grid-column:2;grid-row:1/span 2;}"
    "html.ms9-active #caApp>.caAsideTgl{display:none}"
    "html.ms9-active #caApp #caEmpty:not([hidden]){display:block}"
)
PATCH_JS = (
    'function caMobileReveal(){ try{ if(document.documentElement.classList.contains("ms9-active")) return;}catch(e){} }'
    'function caCollapse(){ if(document.documentElement.classList.contains("ms9-active") || innerWidth>=981) return;}'
)


def fixture():
    return (parent_fixture().replace(b"</style>", PATCH_CSS.encode() + b"</style>")
            .replace(b"</script>", PATCH_JS.encode() + b"</script>"))


class Stage40AtlasHostGate(unittest.TestCase):
    def setUp(self):
        self.active=b"stage39-source-index"
        self.index=fixture()
        self.sources={"stage39":sha(self.active)}
        self.hash=sha(self.index)

    def evaluate(self, *, source=None, candidate=None, extra=()):
        data=self.index if candidate is None else candidate
        contents=[("index.html",data),*extra]
        return check(self.active if source is None else source,
                     make_zip(contents),
                     source_sha256=self.sources,target_sha256=sha(data),
                     expected_assets={})

    def assert_failed_check(self, old, new, check_name):
        self.assertIn(old, self.index)
        altered=self.index.replace(old,new)
        self.assertFalse(self.evaluate(candidate=altered)["checks"][check_name])

    def test_valid_stage40_candidate(self):
        self.assertEqual(set(SOURCE_SHA256),{"original","stage37","stage39"})
        self.assertEqual(TARGET_SHA256,
                         "3b80f0e8db2334e1e0a0febe3acd17f84ba89dcac09b2f1632353f61d8859958")
        result=self.evaluate()
        self.assertTrue(result["pass"],result)
        self.assertFalse(result["deployed"])

    def test_wrong_active_host_rejected(self):
        self.assertFalse(self.evaluate(source=b"hourly-host-update")["checks"]["active_index_pinned"])

    def test_reject_missing_second_atlas_panel_placement(self):
        self.assert_failed_check(b"#caApp>aside#caAside2{grid-row:2}",
                                 b"#caApp>aside#caAside2{grid-row:1}",
                                 "stage40_two_panel_source_rows")

    def test_reject_main_over_settings(self):
        self.assert_failed_check(b"#caApp>main{grid-column:2;grid-row:1/span 2;",
                                 b"#caApp>main{grid-column:1;grid-row:1;",
                                 "stage40_two_panel_source_rows")

    def test_reject_mobile_one_column_reintroduced(self):
        self.assert_failed_check(b"#caApp.wrap:not([hidden]){display:grid;",
                                 b"#caApp.wrap:not([hidden]){display:flex;",
                                 "stage40_two_panel_source_rows")

    def test_reject_auto_collapsed_panels(self):
        self.assert_failed_check(
            b'function caCollapse(){ if(document.documentElement.classList.contains("ms9-active") || innerWidth>=981) return;',
            b'function caCollapse(){ if(innerWidth>=981) return;',
            "stage40_controls_visible_in_r5")

    def test_reject_automatic_mobile_scroll_and_collapse(self):
        self.assert_failed_check(
            b'function caMobileReveal(){ try{ if(document.documentElement.classList.contains("ms9-active")) return;',
            b'function caMobileReveal(){ try{ if(innerWidth>=981) return;',
            "stage40_controls_visible_in_r5")

    def test_reject_mobile_empty_message_loss(self):
        self.assert_failed_check(b"#caApp #caEmpty:not([hidden]){display:block}",
                                 b"#caApp #caEmpty:not([hidden]){display:none}",
                                 "stage40_empty_state_mobile")

    def test_reject_unapproved_php_archive_member(self):
        r=self.evaluate(extra=[("deploy.php",b"do not execute")])
        self.assertFalse(r["checks"]["exact_expected_paths"])

    def test_reject_dangerous_archive_path(self):
        r=self.evaluate(extra=[("../index.html",b"host overwrite")])
        self.assertFalse(r["checks"]["exact_expected_paths"])


if __name__ == "__main__":
    unittest.main()
