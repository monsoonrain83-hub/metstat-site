"""Isolated, standard-library-only MetStat vNext r3 UI contract tests."""
import html.parser
import http.server
import json
import re
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from preview_server import PreviewHandler, ROUTES, ALIASES

ROUTES_JSON = json.loads((ROOT / 'route_catalog.json').read_text(encoding='utf8'))
PALETTES = json.loads((ROOT / 'palettes.json').read_text(encoding='utf8'))
HTML = (ROOT / 'index.html').read_text(encoding='utf8')
CSS = (ROOT / 'styles.css').read_text(encoding='utf8')
JS = (ROOT / 'app.js').read_text(encoding='utf8')


class IdParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.scripts = []
        self.attrs_by_tag = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'script':
            self.scripts.append(a.get('src'))
        self.attrs_by_tag.append((tag, a))


class ShellContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = IdParser()
        cls.p.feed(HTML)

    def test_01_canonical_routes(self):
        self.assertEqual(len(ROUTES_JSON), 43)
        self.assertEqual(len({r['path'] for r in ROUTES_JSON}), 43)
        self.assertEqual(len({r['title'] for r in ROUTES_JSON}), 43)

    def test_02_all_major_sections(self):
        expected = ['خانه', 'پایش و پیش‌بینی', 'جعبه ابزار هواشناسی', 'تحلیل همدیدی', 'اقلیم و ایستگاه‌ها']
        self.assertEqual(set(r['group'] for r in ROUTES_JSON), set(expected))

    def test_03_key_routes(self):
        for slug in ['/monitoring-forecast/weather-models', '/monitoring-forecast/weather-models/custom-multi-model', '/monitoring-forecast/forecast-verification/iranmet-bulletin', '/meteorological-tools/rainfall-isohyet', '/climate-analytics/drought', '/monitoring-forecast/flash-flood']:
            with self.subTest(slug=slug):
                self.assertIn(slug, ROUTES)

    def test_04_ids_unique(self):
        self.assertEqual(len(self.p.ids), len(set(self.p.ids)))

    def test_05_no_remote_script(self):
        self.assertEqual(self.p.scripts, ['route-data.js', 'palette-data.js', 'app.js'])
        self.assertNotIn('https://', HTML)
        self.assertIn("connect-src 'none'", HTML)

    def test_06_pinch_gesture_enabled(self):
        self.assertIn('user-scalable=yes', HTML)
        self.assertIn('maximum-scale=5', HTML)
        self.assertIn('pinch-zoom', CSS)
        self.assertNotIn('touchmove', JS)  # no touch interception blocks native pinch

    def test_07_fills_landscape(self):
        self.assertIn('height:100dvh', CSS)
        self.assertIn('@media(max-height:480px)', CSS)
        self.assertIn('.app{min-height:0}', CSS)
        self.assertNotIn('min-height:560px', CSS)

    def test_08_model_symbols_are_compact(self):
        self.assertIn('className=\'model-status\'', JS)
        self.assertIn('width:46px;height:40px', CSS)
        self.assertNotIn('width:138px', CSS)
        self.assertIn('GEM / GDPS', JS)
        self.assertIn('ECMWF EC46', JS)

    def test_09_independent_model_status_colors(self):
        for color in ['#17b486', '#eb5569', '#448bda', '#e9b443']:
            self.assertIn(color, CSS)
        self.assertIn('[data-status="updating"]', CSS)

    def test_10_full_custom_mode_and_restore(self):
        self.assertIn("function modeSwitchCustom()", JS)
        self.assertIn("function modeSwitchForecast()", JS)
        self.assertIn('state.lastForecast', JS)
        self.assertIn('data-mode="custom"', CSS)
        self.assertIn('customGenerate', JS)

    def test_11_multimodel_scope(self):
        self.assertIn("['00','06','12','18']", JS)  # daily forecast runs
        self.assertIn("60,gfs:15,icon:10,gem:8,ukmo:7", JS)
        self.assertIn("!['iri','aifs','arpege'].includes", JS)
        self.assertIn('ECMWF', JS)

    def test_12_visual_export_dialog(self):
        for i in ['exportDialog', 'gifDialog', 'pngScale', 'gifFps', 'gifFrom', 'gifTo', 'gifLoop', 'saveBtn']:
            self.assertIn(i, self.p.ids)
        self.assertIn('canvas.toBlob', JS)
        self.assertIn('DEMO_NOT_FORECAST.png', JS)

    def test_13_forecast_slider(self):
        for i in ['leadRange', 'leadPrev', 'leadNext', 'leadPlay', 'leadStep']:
            self.assertIn(i, self.p.ids)
        self.assertIn('state.availableLeads', JS)

    def test_14_layers_and_labels(self):
        for field in ['مرز شهرستان‌ها', 'نقاط روستایی', 'دریاچه‌ها', 'رودخانه‌ها', 'راه‌ها و بزرگراه‌ها', 'پایتخت‌های جهان', 'اندازه برچسب', 'ضخامت خطوط']:
            self.assertIn(field, JS)

    def test_15_palette_integrity(self):
        self.assertEqual(len(PALETTES['palettes']), 41)
        self.assertEqual(len(PALETTES['edges']), 26)
        self.assertIn('MT_PALS', (ROOT / 'palette-data.js').read_text())
        self.assertIn('renderPaletteTicks', JS)

    def test_16_color_theme(self):
        for color in ['#399FD4', '#F8F9FD', '#DC1937']:
            self.assertIn(color.upper(), CSS.upper())
        self.assertIn('background:#0b6b9b', CSS)

    def test_17_map_controls_no_expand_tooltips(self):
        for i in ['zoomIn', 'zoomOut', 'fullExtent', 'refreshMap', 'layersBtn', 'windBtn']:
            self.assertIn(i, self.p.ids)
        self.assertIn('class="map-left-rail"', HTML)
        self.assertIn('class="map-save"', HTML)

    def test_18_all_legacy_homepage_functions(self):
        required = ['WeatherBELL', 'weather.us', 'tropicaltidbits', 'weathermodels', 'اصلاح ارتفاعی', 'همرفت', 'تراکم رعدوبرق', 'شاخص‌های اقلیمی', 'اطلس اقلیمی', 'خشکسالی', 'هم‌بارش', 'پایش دقت مدل‌ها']
        titles = ' '.join(x['title'] for x in ROUTES_JSON)
        for name in required:
            with self.subTest(name=name):
                self.assertIn(name, titles)

    def test_19_single_header_and_stable_chrome(self):
        self.assertEqual(HTML.count('class="header"'), 1)
        self.assertEqual(HTML.count('class="map-card"'), 1)
        self.assertEqual(HTML.count('class="map-save"'), 1)
        self.assertIn('grid-template-columns:328px minmax(0,1fr)', CSS)

    def test_20_read_only_no_network(self):
        self.assertNotIn('fetch(', JS)
        self.assertNotIn('XMLHttpRequest', JS)
        self.assertNotIn('eval(', JS)
        self.assertNotIn('document.write(', JS)


class LocalPreviewRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = http.server.ThreadingHTTPServer(('127.0.0.1', 0), PreviewHandler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:%d' % cls.http.server_port

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join(timeout=2)

    def test_21_all_routes_independently_200(self):
        for slug in sorted(ROUTES):
            with self.subTest(slug=slug), urlopen(self.url + slug, timeout=4) as res:
                self.assertEqual(res.status, 200)
                self.assertIn('text/html', res.headers.get('Content-Type', ''))
                self.assertIn(b'MetStat', res.read(700))

    def test_22_legacy_aliases_remain_previewable(self):
        for slug in ALIASES:
            with self.subTest(slug=slug), urlopen(self.url + slug, timeout=3) as res:
                self.assertEqual(res.status, 200)

    def test_23_unknown_routes_and_traversal_blocked(self):
        for slug in ['/unknown', '/monitoring-forecast/404', '/../etc/passwd', '/wp-admin', '/assets/nope.svg']:
            with self.subTest(slug=slug), self.assertRaises(HTTPError) as e:
                urlopen(self.url + slug, timeout=3)
            self.assertEqual(e.exception.code, 404)

    def test_24_security_headers(self):
        with urlopen(self.url + '/app.js', timeout=4) as res:
            self.assertEqual(res.headers['X-Content-Type-Options'], 'nosniff')
            self.assertEqual(res.headers['X-Frame-Options'], 'DENY')
            self.assertIn("connect-src 'none'", res.headers['Content-Security-Policy'])


if __name__ == '__main__':
    unittest.main(verbosity=2)