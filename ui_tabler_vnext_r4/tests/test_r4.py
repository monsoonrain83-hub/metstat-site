"""Structural, offline and preview-route guards for MetStat vNext r4.
These are NOT production integration or meteorological accuracy tests.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
import socket
import time
from contextlib import closing

ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'route_catalog.json').read_text(encoding='utf8'))
HTML=(ROOT/'index.html').read_text(encoding='utf8')
CSS=(ROOT/'styles.css').read_text(encoding='utf8')
APP=(ROOT/'app.js').read_text(encoding='utf8')
ACC=(ROOT/'account-r4.js').read_text(encoding='utf8')
DRAW=(ROOT/'drawing-r4.js').read_text(encoding='utf8')

class StructuralTests(unittest.TestCase):
    def test_unique_valid_catalog(self):
        routes=[p['path'] for p in CAT]
        self.assertEqual(len(routes),63)
        self.assertEqual(len(routes),len(set(routes)))
        self.assertTrue(all(x.startswith('/') and '//' not in x and '..' not in x for x in routes))
    def test_parent_paths_are_real(self):
        routes={p['path'] for p in CAT}
        for p in CAT:
            if p['parent_path'] is not None:
                with self.subTest(p=p['path']):self.assertIn(p['parent_path'],routes)
    def test_provenance_is_disclosed(self):
        for p in CAT:
            self.assertIn('legacy_source',p)
            self.assertIn('origin',p)
            self.assertFalse(p['route_verified_live'])
    def test_main_nav_five_source_categories(self):
        for label in ('پایش و پیش‌بینی','هواشناسی کاربردی','تحلیل همدیدی','جعبه ابزار هواشناسی','هسته تحلیل اقلیم'):
            self.assertIn(label,APP)
        self.assertIn('data-nav-trigger',APP)
        self.assertIn('<details',APP)
    def test_account_panel_and_roles(self):
        for part in ('accountToggle','accountDropdown','accountView','accountStageDetails'):
            self.assertIn('id="'+part+'"',HTML)
        self.assertIn('connected:false',ACC)
        self.assertIn('input.disabled=true',ACC)
        self.assertIn('role=\'guest\'',ACC)
        self.assertIn('lastNonAccount',ACC)
    def test_account_roles_and_screens_present(self):
        names=('ورود','ثبت‌نام','علاقه‌مندی‌ها','ویرایش حساب','پنل مدیر','تأیید آمار ماهانه')
        for label in names:self.assertIn(label,ACC)
        for suffix in ('login','register','favorites','profile','admin','station-approval'):
            self.assertIn('/account/'+suffix,[r['path'] for r in CAT])
    def test_draw_toolbar_fronts_shapes_and_history(self):
        for tool in ('ruler','solid','dash','arrow','cold','warm','occl','stat','rect','circ','free','dot','text'):
            self.assertIn('data-draw="'+tool+'"',HTML)
        for elem in ('drawUndo','drawRedo','drawingOverlay','drawingToggle','drawTextDialog'):
            self.assertIn('id="'+elem+'"',HTML)
        self.assertIn('data-draw-capture',DRAW)
        self.assertIn('pointerdown',DRAW)
        self.assertIn('pointerup',DRAW)
        self.assertIn('touch-action:none',CSS)
    def test_drawing_not_geodesic_claim(self):
        self.assertIn('بدون مختصات واقعی',HTML)
        self.assertIn('NO FORECAST DATA',HTML)
    def test_isolated_forecast_status_colors(self):
        self.assertIn('map-right-rail',HTML)
        self.assertIn('.account-view',CSS)
        self.assertIn('#accountView{transition:none!important;opacity:1!important}',CSS)
        self.assertIn('data-mode="account"',CSS)
    def test_no_external_network_and_untrusted_dynamic_markup(self):
        self.assertIn('connect-src \'none\'',HTML)
        self.assertNotIn('fetch(',ACC)
        self.assertNotIn('localStorage',ACC)
        self.assertNotIn('eval(',DRAW)
        self.assertNotIn('innerHTML',ACC)
    def test_offline_bundle_is_inline_and_preview_only(self):
        p=ROOT/'MetStat_vNext_r4_ALL_PAGES_USER_DRAWING_INTERACTIVE_OFFLINE.html'
        self.assertTrue(p.is_file())
        s=p.read_text(encoding='utf8')
        self.assertGreater(len(s),190000)
        self.assertNotIn('src="app.js"',s)
        self.assertNotIn('href="styles.css"',s)
        self.assertIn('data:image/webp;base64,',s)
        self.assertIn('connect-src \'none\'',s)
    def test_source_JS_syntax(self):
        for f in ('route-data.js','palette-data.js','app.js','account-r4.js','drawing-r4.js'):
            c=subprocess.run(['node','--check',str(ROOT/f)],capture_output=True,text=True)
            self.assertEqual(c.returncode,0,c.stderr)
    def test_palette_source_valid(self):
        p=json.loads((ROOT/'palettes.json').read_text(encoding='utf8'))
        self.assertEqual(len(p['palettes']),41)
        self.assertEqual(len(p['edges']),26)

class PreviewHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with closing(socket.socket(socket.AF_INET,socket.SOCK_STREAM)) as sock:
            sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1]
        cls.proc=subprocess.Popen([sys.executable,str(ROOT/'preview_server.py'),'--port',str(cls.port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                with urlopen(f'http://127.0.0.1:{cls.port}/',timeout=.25) as r:
                    if r.status==200:return
            except Exception:time.sleep(.02)
        raise RuntimeError('preview HTTP server startup failed')
    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:cls.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:cls.proc.kill()
    def test_all_63_routes_are_directly_reachable(self):
        for p in CAT:
            with self.subTest(route=p['path']):
                with urlopen(f"http://127.0.0.1:{self.port}{p['path']}",timeout=2) as resp:
                    self.assertEqual(resp.status,200)
                    self.assertIn(b'<!doctype html>',resp.read(35).lower())
    def test_known_legacy_alias_and_unrecognized_404(self):
        with urlopen(f'http://127.0.0.1:{self.port}/monitoring-forecast/weather-models/online-maps') as resp:
            self.assertEqual(resp.status,200)
        for path in ('/private/config.php','/this-route-does-not-exist','/vnext.secret'):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as e:urlopen(f'http://127.0.0.1:{self.port}{path}',timeout=2)
                self.assertEqual(e.exception.code,404)
    def test_five_assets_are_local(self):
        for name in ('account-r4.js','drawing-r4.js','styles.css','palette-data.js','assets/homepage_atmosphere.webp'):
            with self.subTest(name=name):
                with urlopen(f'http://127.0.0.1:{self.port}/{name}',timeout=2) as r:
                    self.assertEqual(r.status,200)
                    self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff')
if __name__=='__main__': unittest.main(verbosity=2)