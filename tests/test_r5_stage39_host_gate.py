"""Stage39 original-R5 two-column host overlay safety regression (no deployment)."""
from io import BytesIO
import unittest
from zipfile import ZipFile
from tools.r5_stage39_host_gate import check, sha, SOURCE_SHA256, TARGET_SHA256
from tests.test_r5_stage37_host_gate import fixture as base_fixture

CSS = (
    'html.ms9-active #ciMain{display:grid;grid-template-columns:var(--ms9-sidebar-width,328px) minmax(0,1fr)}'
    '@media (orientation:landscape){html.ms9-active{--ms9-sidebar-width:230px}}'
    'html.ms9-active #labApp .lab>.labIn{grid-column:1}'
    'html.ms9-active #synApp .synCard{display:grid}'
    'html.ms9-active #fontBtn{position:fixed;inset-inline-end:4px;bottom:190px}'
)

def fixture():
    return base_fixture().replace(b'</style>', CSS.encode() + b'</style>')

def zipfile(members):
    b = BytesIO()
    with ZipFile(b, 'w') as z:
        for name, content in members:
            z.writestr(name, content)
    return b.getvalue()

class Stage39GateTest(unittest.TestCase):
    def setUp(self):
        self.original = b'base-stage37-index'
        self.candidate = fixture()
        self.index_hash = sha(self.candidate)
        self.src_hash = {'stage37': sha(self.original)}
        self.archive = zipfile([('index.html', self.candidate)])

    def check(self, data=None, candidate=None, baseline=None, src_hash=None, assets=None):
        return check(self.original if baseline is None else baseline,
            self.archive if data is None else data,
            source_sha256=self.src_hash if src_hash is None else src_hash,
            target_sha256=self.index_hash if candidate is None else sha(candidate),
            expected_assets={} if assets is None else assets)

    def modified(self, before, after):
        candidate = self.candidate.replace(before.encode(), after.encode())
        return self.check(data=zipfile([('index.html', candidate)]), candidate=candidate)

    def test_real_pinned_sources_only(self):
        self.assertEqual(set(SOURCE_SHA256), {'original','stage37'})
        self.assertEqual(TARGET_SHA256,'9dc68b50c2e8817e8e1b9996d8fd7d48f6defd016aca0a8cdd9a10c949d93e0e')
        self.assertTrue(self.check()['pass'], self.check())

    def test_reject_unsupported_active_version(self):
        self.assertFalse(self.check(baseline=b'unknown')['pass'])

    def test_reject_different_candidate_sha(self):
        self.assertFalse(self.check(candidate=b'unexpected')['pass'])

    def test_reject_one_column(self):
        r = self.modified('grid-template-columns:var(--ms9-sidebar-width,328px) minmax(0,1fr)', 'grid-template-columns:1fr')
        self.assertFalse(r['checks']['stage39_right_panel'])

    def test_reject_missing_short_landscape_sidebar(self):
        r = self.modified('--ms9-sidebar-width:230px','--ms9-sidebar-width:400px')
        self.assertFalse(r['checks']['stage39_right_panel'])

    def test_reject_analysis_page_owner_loss(self):
        r = self.modified('#labApp .lab>.labIn','#labApp .lab>.bad')
        self.assertFalse(r['checks']['stage39_lab_synoptic'])

    def test_reject_a11y_overlap_regression(self):
        r = self.modified('inset-inline-end:4px;bottom:190px','inset-inline-start:4px;bottom:102px')
        self.assertFalse(r['checks']['stage39_original_a11y_button'])

    def test_reject_three_column_atlas(self):
        original = b'grid-template-columns:minmax(260px,310px) minmax(260px,310px) minmax(0,1fr)'
        candidate = self.candidate.replace(b'</style>', original + b'</style>')
        r = self.check(data=zipfile([('index.html',candidate)]),candidate=candidate)
        self.assertFalse(r['checks']['stage39_no_atlas_three_columns'])

    def test_reject_unknown_php_or_directory_traversal(self):
        for name in ('upload.php','../index.html'):
            with self.subTest(name=name):
                r = self.check(data=zipfile([('index.html',self.candidate),(name,b'oops')]))
                self.assertFalse(r['checks']['exact_expected_paths'])

    def test_reject_original_without_matching_asset_members(self):
        r = self.check(src_hash={'original':sha(self.original)},
                       assets={'assets/metstat_map_ui_r201.js':sha(b'R201')})
        self.assertFalse(r['checks']['exact_expected_paths'])

    def test_zip_crc_and_duplicate_protection(self):
        self.assertFalse(self.check(data=b'not zip')['pass'])
        r=self.check(data=zipfile([('index.html',self.candidate),('index.html',self.candidate)]))
        self.assertFalse(r['checks']['unique_zip_members'])

if __name__ == '__main__':
    unittest.main()
