"""Isolated smoke/structure/security checks; NOT a production browser E2E test."""
import contextlib
import json
import socket
import subprocess
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from bs4 import BeautifulSoup
import tinycss2

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from preview_server import PreviewHandler, ROUTES  # noqa: E402


class StructureChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (BASE / 'index.html').read_text(encoding='utf8')
        cls.css = (BASE / 'theme.css').read_text(encoding='utf8')
        cls.js = (BASE / 'app.js').read_text(encoding='utf8')
        cls.dom = BeautifulSoup(cls.html, 'html.parser')

    def test_unique_dom_ids(self):
        ids=[node['id'] for node in self.dom.select('[id]')]
        self.assertEqual(len(ids),len(set(ids)))
        for target in self.dom.select('[aria-controls]'):
            self.assertIn(target['aria-controls'],ids)

    def test_five_geo_selects_in_one_bar_in_correct_order(self):
        bar=self.dom.select_one('.ms-geo-bar')
        self.assertIsNotNone(bar)
        self.assertEqual([x['id'] for x in bar.select('select')],
            ['msContinent','msRegion','msCountry','msProvince','msCounty'])
        self.assertIn('grid-template-columns:120px repeat(5',self.css)

    def test_forecast_and_map_controls_are_separate_groups(self):
        forecast=self.dom.select_one('.ms-forecast')
        self.assertEqual(len(forecast.select('[data-period]')),5)
        self.assertEqual(len(forecast.select('#msModel,#msMainParameter,#msSecondaryParameter,#msRun,#msLead')),5)
        self.assertIsNotNone(self.dom.select_one('.ms-map-surface .ms-overlay-group'))
        self.assertIsNotNone(self.dom.select_one('.ms-map-surface #msLayerPanel'))
        self.assertEqual(len(self.dom.select('.ms-map-surface #msModelRail')),1)
        self.assertEqual(len(self.dom.select('.ms-map-surface .ms-map-left-rail')),1)
        self.assertIn('min-width:1180px',self.css)
        self.assertNotIn('grid-template-columns:1fr;',self.css)

    def test_original_priority_and_presentation(self):
        buttons=[x.get('data-action') for x in self.dom.select('.ms-map-left-rail button')]
        self.assertEqual(buttons,['zoom-in','zoom-out','extent','refresh'])
        model_buttons=self.dom.select('.ms-model-rail [data-quick-model]')
        self.assertEqual([x['data-quick-model'] for x in model_buttons],
                         ['ecmwf','gfs','icon','gem','ukmo'])
        self.assertIn('data-status="updating"',self.html)
        self.assertIn('@media(prefers-reduced-motion:reduce)',self.css)
        self.assertIn('overflow-x:auto',self.css)

    def test_prevents_fake_data_and_untrusted_network(self):
        self.assertIn('NO MODEL DATA',self.html)
        self.assertIn('داده زنده متصل نیست',self.html)
        self.assertEqual(self.dom.select_one('meta[http-equiv="Content-Security-Policy"]').get('content').split('connect-src ')[1].split(';')[0],"'none'")
        for asset in self.dom.select('script[src],link[href]'):
            src=asset.get('src',asset.get('href'))
            self.assertFalse(src.startswith(('http:','https:','//')))
        self.assertNotIn('innerHTML',self.js)
        self.assertNotIn('eval(',self.js)
        self.assertNotIn('setInterval(',self.js)
        self.assertNotIn('fetch(',self.js)

    def test_css_parses_without_syntax_errors(self):
        rules=tinycss2.parse_stylesheet(self.css,skip_whitespace=True,skip_comments=True)
        self.assertFalse([n for n in rules if n.type=='error'])
        self.assertGreater(len(rules),60)

    def test_javascript_syntax(self):
        r=subprocess.run(['node','--check',str(BASE/'app.js')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_routes_have_all_expected_tabs_and_navigation(self):
        routes=json.loads((BASE/'routes.json').read_text(encoding='utf8'))
        self.assertEqual(set(routes['canonical_routes']),ROUTES)
        self.assertEqual(len(routes['canonical_routes']),len(set(routes['canonical_routes'])))
        for url in routes['canonical_routes']:
            self.assertIn(url,self.js)
        self.assertIn('/monitoring-forecast/weather-models/online-maps',routes['provisional_legacy_aliases'])
        for a in self.dom.select('a[data-route]'):
            self.assertIn(a['href'],ROUTES)
        self.assertIn("window.addEventListener('popstate'",self.js)
        self.assertIn("e.key==='Escape'",self.js)

    def test_accessibility_controls(self):
        for btn in self.dom.select('button'):
            self.assertEqual(btn.get('type'), 'button', str(btn)[:150])
            self.assertTrue(btn.get('aria-label') or btn.get_text(strip=True) or btn.select_one('svg'), str(btn))
        for item in self.dom.select('select'):
            self.assertTrue(item.get('aria-label') or self.dom.find('label', attrs={'for':item['id']}),str(item))
        self.assertIsNotNone(self.dom.select_one('#msActionStatus[aria-live="polite"]'))
        self.assertIsNotNone(self.dom.select_one('button[data-action="layers"][aria-expanded]'))


class RouteServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),PreviewHandler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)

    def test_deep_routes_can_reload_directly(self):
        for path in sorted(ROUTES):
            with self.subTest(path=path):
                with urlopen(self.base+path,timeout=4) as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b'MetStat',r.read(1200))

    def test_unknown_and_old_url_not_silently_rewritten(self):
        for path in ['/private/secret.php','/a-bogus-route',
                     '/monitoring-forecast/weather-models/online-maps']:
            with self.subTest(path=path),self.assertRaises(HTTPError) as caught:
                urlopen(self.base+path,timeout=4)
            self.assertEqual(caught.exception.code,404)

    def test_assets_are_served_with_content_type_guard(self):
        for path in ['/theme.css','/app.js']:
            with urlopen(self.base+path,timeout=4) as r:
                self.assertEqual(r.status,200)
                self.assertEqual(r.headers.get('X-Content-Type-Options'),'nosniff')


if __name__=='__main__': unittest.main()
