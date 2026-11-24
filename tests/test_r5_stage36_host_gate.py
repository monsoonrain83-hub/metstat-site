"""Stage36 source-pinned host release gate regression, no actual deployment."""
from hashlib import sha256
from io import BytesIO
import unittest
from zipfile import ZipFile

from tools.r5_stage36_host_gate import check, sha


def fixture():
    source = (
        '<!doctype html><html><head><style>' +
        '/*guard*/' + 'a{color:red!important}' * 1138 +
        '</style></head><body><div id="onAside"></div>'
        '<div id="onEmpty"></div><div id="onViewer" hidden></div>'
        '<script>const a="metstat:nv-model-options";'
        'const b="metstat:nv-model-options";'
        'document.addEventListener(\'langchange\',syncGeo);'
        'if(st.__msNvPointerBound) return;'
        'NV.resizeObserver.disconnect(); NV.resizeObserver=null;'
        'NVF.on=true; nvfBtnLab(); NVF.on=false; nvfBtnLab();'
        '</script>'
        '</body></html>'
    )
    assert len(source.encode()) > 1024
    return source.encode()


def zip_bytes(members):
    b = BytesIO()
    with ZipFile(b, "w") as z:
        for path, blob in members:
            z.writestr(path, blob)
    return b.getvalue()


class Stage36HostGateTest(unittest.TestCase):
    def setUp(self):
        self.active = b'previous-stage35-index'
        self.index = fixture()
        self.zip = zip_bytes([('index.html', self.index)])
        self.src_hashes = {'stage35': sha(self.active)}
        self.target_hash = sha(self.index)

    def evaluate(self, *, active=None, index=None, data=None, sources=None, target=None):
        return check(self.active if active is None else active,
                     self.zip if data is None else data,
                     source_sha256=self.src_hashes if sources is None else sources,
                     target_sha256=self.target_hash if target is None else target,
                     expected_assets={})

    def test_valid_pinned_incremental_zip(self):
        r = self.evaluate()
        self.assertTrue(r['pass'], r)
        self.assertEqual(r['source_kind'], 'stage35')
        self.assertFalse(r['deployed'])

    def test_unknown_baseline_rejected(self):
        self.assertFalse(self.evaluate(active=b'unknown')['checks']['active_index_pinned'])

    def test_wrong_candidate_sha_rejected(self):
        self.assertFalse(self.evaluate(target='0'*64)['checks']['candidate_index_sha'])

    def test_unexpected_php_rejected(self):
        data = zip_bytes([('index.html', self.index), ('install.php', b'a')])
        self.assertFalse(self.evaluate(data=data)['checks']['exact_expected_paths'])

    def test_zip_path_escape_rejected(self):
        data = zip_bytes([('index.html', self.index), ('../index.html', b'x')])
        self.assertFalse(self.evaluate(data=data)['checks']['exact_expected_paths'])

    def test_duplicate_member_rejected(self):
        data = zip_bytes([('index.html', self.index), ('index.html', self.index)])
        self.assertFalse(self.evaluate(data=data)['checks']['unique_zip_members'])

    def test_wrong_index_dom_id_rejected(self):
        modified = self.index.replace(b'</body>', b'<div id="onAside"></div></body>')
        data = zip_bytes([('index.html', modified)])
        r = self.evaluate(data=data, target=sha(modified))
        self.assertFalse(r['checks']['unique_dom_ids'])

    def test_missing_lang_event_rejected(self):
        modified = self.index.replace(b'langchange', b'other-event')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['stage36_events'])

    def test_poll_reintroduced_rejected(self):
        modified = self.index.replace(b'</body>', b'setInterval(badgeModel,1800)</body>')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['poll_removed'])

    def test_important_rule_count_guard(self):
        modified = self.index.replace(b'</style>', b'!important</style>')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['no_added_important'])

    def test_original_requires_exact_assets(self):
        src = {'original': sha(self.active)}
        r = self.evaluate(sources=src)
        self.assertTrue(r['pass'], r)  # With empty override, no required assets.
        assets = {'assets/a.js': sha(b'safe')}
        r2 = check(self.active, self.zip, source_sha256=src,
                   target_sha256=self.target_hash, expected_assets=assets)
        self.assertFalse(r2['checks']['exact_expected_paths'])

    def test_rejects_double_bound_pointer_owner(self):
        modified = self.index.replace(b'if(st.__msNvPointerBound) return;', b'if(false) return;')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['pointer_single_owner'])

    def test_rejects_missing_observer_cleanup(self):
        modified = self.index.replace(b'NV.resizeObserver.disconnect(); NV.resizeObserver=null;', b'NV.resizeObserver.disconnect();')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['observer_leaves_clean'])

    def test_rejects_fullscreen_polling(self):
        modified = self.index.replace(b'</script>', b'setInterval(nvfBtnLab,600);</script>')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['no_fullscreen_label_poll'])

    def test_rejects_fullscreen_label_stale(self):
        modified = self.index.replace(b'NVF.on=true; nvfBtnLab();', b'NVF.on=true;')
        data = zip_bytes([('index.html', modified)])
        self.assertFalse(self.evaluate(data=data, target=sha(modified))['checks']['fullscreen_label_transitions'])

    def test_corrupt_zip_rejected(self):
        self.assertFalse(self.evaluate(data=b'not a ZIP')['pass'])


if __name__ == '__main__':
    unittest.main()
