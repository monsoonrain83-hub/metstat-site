"""Stage41 reject negative keyboard/semantic state regressions in original host ZIP."""
import unittest
from tools.r5_stage41_host_gate import check, sha, SOURCE_SHA256, TARGET_SHA256
from test_r5_stage40_host_gate import fixture as previous_fixture
from test_r5_stage39_host_gate import zipfile as make_zip

SCRIPT_MARKERS = (
    'h.setAttribute("role","button");'
    'h.setAttribute("aria-expanded",String(!c.classList.contains("pcol")));'
    'h.onkeydown=e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); toggle(); } };'
    'const key=c.classList.contains("sfSet")?"settings":c.querySelector("#sfIdxTab")?"indices":"method";'
    'Object.prototype.hasOwnProperty.call(SF.col,key)?SF.col[key]:!(key==="settings"||key==="forecast");'
)
CSS_MARKERS = (
    'html.ms9-active #caApp .panel>h2:focus-visible,'
    'html.ms9-active #sfMain .card>h3:focus-visible'
)

def fixture():
    return (previous_fixture().replace(b"</script>", SCRIPT_MARKERS.encode()+"\n".encode()+b"</script>")
            .replace(b"</style>", CSS_MARKERS.encode()+b"</style>"))


class Stage41InteractionGate(unittest.TestCase):
    def setUp(self):
        self.active=b'stage40-verified-source-index'
        self.index=fixture()
        self.hash=sha(self.index)

    def check(self, candidate=None, baseline=None, extra=()):
        candidate=self.index if candidate is None else candidate
        return check(self.active if baseline is None else baseline,
                     make_zip([('index.html',candidate),*extra]),
                     source_sha256={'stage40':sha(self.active)},
                     target_sha256=sha(candidate), expected_assets={})

    def reject(self, old, new, key):
        self.assertIn(old,self.index)
        mutated=self.index.replace(old,new)
        self.assertFalse(self.check(candidate=mutated)['checks'][key])

    def test_pinned_stage41_target_and_allowed_sources(self):
        self.assertEqual(set(SOURCE_SHA256),{'original','stage37','stage39','stage40'})
        self.assertEqual(TARGET_SHA256,'7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295')
        self.assertTrue(self.check()['pass'],self.check())

    def test_unknown_live_index_refused(self):
        self.assertFalse(self.check(baseline=b'hourly-unknown')['checks']['active_index_pinned'])

    def test_missing_accessible_panel_roles_rejected(self):
        self.reject(b'h.setAttribute("role","button")',b'/* missing role */','stage41_accessible_native_atlas')

    def test_missing_enter_space_rejected(self):
        self.reject(b'h.onkeydown=e=>{ if(e.key==="Enter"||e.key===" ")',
                    b'h.onkeydown=e=>{ if(e.key==="Escape")','stage41_accessible_native_atlas')

    def test_translated_title_as_state_key_rejected(self):
        self.reject(b'c.classList.contains("sfSet")?"settings"',
                    b'h.textContent.trim().slice(0,30)?"settings"','stage41_seasonal_semantic_keys')

    def test_settings_start_hidden_regression_rejected(self):
        self.reject(b'!(key==="settings"||key==="forecast")',
                    b'!(key==="forecast")','stage41_seasonal_semantic_keys')

    def test_no_visible_focus_rejected(self):
        self.reject(b'html.ms9-active #sfMain .card>h3:focus-visible',
                    b'html.ms9-active #sfMain .card>h3:hover','stage41_focus_visible')

    def test_preexisting_atlas_two_rows_required(self):
        self.reject(b'#caApp>aside#caAside2{grid-row:2}',
                    b'#caApp>aside#caAside2{grid-row:1}','stage40_two_panel_source_rows')

    def test_preexisting_image_retry_required(self):
        self.reject(b'if(!img && NV.cache.get(url)===p) NV.cache.delete(url);',
                    b'/* permanently cache failed image */','stage37_network_retry')

    def test_forbid_new_php_or_traversal_members(self):
        for name in ('deploy.php','../index.html'):
            with self.subTest(name=name):
                self.assertFalse(self.check(extra=[(name,b'surprise')])['checks']['exact_expected_paths'])

if __name__ == '__main__':
    unittest.main()
