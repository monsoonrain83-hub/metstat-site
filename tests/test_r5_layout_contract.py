"""R5 contract regression tests; no network or project archives required."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import warnings
from zipfile import ZipFile

from tools.r5_layout_contract import analyze, load_source, main


GOOD = b'''<!doctype html><html lang="fa" dir="rtl"><head><style>
:root{--sky:#399FD4;--paper:#F8F9FD;--scarlet:#DC1937;--ink:#183b53;--muted:#577489;--bg:#eaf4fa;--line:#c2dfed;--panel-font:14px}
.app{min-width:960px}.workspace{display:grid;grid-template-columns:328px minmax(0,1fr)}
</style></head><body><div class="app" data-mode="forecast">
<header class="header"><div class="header-tools"><button id="soundBtn"></button><button id="uiSmaller"></button><button id="uiBigger"></button></div></header>
<div class="title-strip"></div><section class="geo-bar">
<select id="geoContinent"></select><select id="geoRegion"></select><select id="geoCountry"></select><select id="geoProvince"></select><select id="geoCounty"></select></section>
<main class="workspace"><aside class="sidebar"></aside><section class="content"><div class="map-card"><div class="map-stage"></div></div></section></main></div></body></html>'''


class R5Contract(unittest.TestCase):
    def test_reference_shape_passes(self):
        self.assertTrue(analyze(GOOD)["passed"])

    def test_rejects_sidebar_stacked(self):
        s = GOOD.replace(b"328px minmax(0,1fr)", b"1fr")
        self.assertIn("right_sidebar_328", analyze(s)["failed"])

    def test_rejects_fake_markers_in_comments(self):
        s = GOOD.replace(b'<section class="geo-bar">', b'<section>') + b'<!-- geo-bar geoCounty -->'
        self.assertIn("five_real_geo_controls", analyze(s)["failed"])
        self.assertIn("r5_region_order", analyze(s)["failed"])

    def test_rejects_duplicate_dom_id(self):
        s = GOOD.replace(b'<button id="soundBtn"></button>', b'<button id="soundBtn"></button><b id="soundBtn"></b>')
        self.assertIn("no_duplicate_dom_ids", analyze(s)["failed"])

    def test_rejects_missing_geo_level(self):
        self.assertIn("five_real_geo_controls", analyze(GOOD.replace(b'<select id="geoCounty"></select>', b''))["failed"])

    def test_rejects_wrong_r5_palette(self):
        self.assertIn("r5_reference_tokens", analyze(GOOD.replace(b'#DC1937', b'#333333'))["failed"])

    def test_staged_zip_input_no_extraction(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / 'stage.zip'
            with ZipFile(archive, 'w') as z:
                z.writestr('index.html', GOOD)
            self.assertEqual(load_source(archive), GOOD)
            self.assertEqual(main([str(archive)]), 0)

    def test_zip_rejects_duplicate_root_index(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / 'stage.zip'
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with ZipFile(archive, 'w') as z:
                    z.writestr('index.html', GOOD)
                    z.writestr('index.html', GOOD)
            with self.assertRaises(ValueError):
                load_source(archive)

    def test_rejects_bad_pin(self):
        with TemporaryDirectory() as directory:
            html = Path(directory) / 'index.html'
            html.write_bytes(GOOD)
            self.assertEqual(main([str(html), '--expected-index-sha256', '0' * 64]), 1)


if __name__ == '__main__':
    unittest.main()
