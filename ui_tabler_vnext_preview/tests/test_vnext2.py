"""Tabler sky/scarlet UI: read-only, data-accurate and non-invasive integration guards."""
from pathlib import Path
from bs4 import BeautifulSoup
import json, re, subprocess, unittest
import tinycss2
BASE=Path(__file__).resolve().parents[1]
class NewShell(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=(BASE/'index.html').read_text(encoding='utf8')
  cls.css=(BASE/'vnext2.css').read_text(encoding='utf8')
  cls.js=(BASE/'vnext2.js').read_text(encoding='utf8')
  cls.data=json.loads((BASE/'palettes.json').read_text(encoding='utf8'))
  cls.dom=BeautifulSoup(cls.html,'html.parser')
 def test_user_theme_exact_and_model_status_unchanged(self):
  for token in ['#399FD4','#F8F9FD','#DC1937']:self.assertIn(token,self.css)
  self.assertNotIn('.ms-rail-chip{',self.css)
  self.assertNotIn('.ms-rail-chip[data-status=',self.css)
  self.assertIn('ms-rail-chip[data-status="ready"]', (BASE/'theme.css').read_text())
 def test_top_nav_only_with_click_dropdown_subpages(self):
  self.assertEqual(len(self.dom.select('.ms-nav > .ms-nav-group')),4)
  self.assertEqual(len(self.dom.select('button[data-menu-trigger][aria-expanded="false"]')),4)
  self.assertFalse(self.dom.select('.ms-nav > a[data-route]'))
  self.assertGreaterEqual(len(self.dom.select('.ms-nav-menu[hidden] a[data-route]')),7)
  self.assertIn("e.target.closest('[data-menu-trigger]')",self.js)
 def test_disclosure_plus_minus_in_both_parameter_groups(self):
  for t in ('Main','Secondary'):
   p=self.dom.select_one('#msParamPanel'+t)
   self.assertIsNotNone(p)
   self.assertGreaterEqual(len(p.select('details summary')),2)
  self.assertIn("content:'+'",self.css);self.assertIn("content:'−'",self.css)
  self.assertNotRegex(self.js,r'\.innerHTML\s*=')
 def test_single_compact_forecast_timeline(self):
  self.assertEqual(len(self.dom.select('.ms-map-card .ms-forecast-track')),1)
  self.assertFalse(self.dom.select('.ms-forecast > .ms-timeline'))
  for target in ('msLead','msLeadRange','msLeadText','msStepSize','msTimelinePlay'):
   self.assertEqual(len(self.dom.select('#'+target)),1)
  self.assertIn('function stopPlayback()',self.js)
 def test_palette_data_are_verified_existing_site_values(self):
  d=self.data
  self.assertIn('MT_PALS',d['origin']);self.assertGreaterEqual(len(d['palettes']),39)
  self.assertGreaterEqual(len(d['groups']),15)
  self.assertEqual(d['palettes']['wu_total'][0],'#f0f0f0')
  self.assertEqual(d['edges']['wu_total'][-1],500)
  for k,pal in d['palettes'].items():
   self.assertTrue(all(re.fullmatch('#[0-9A-Fa-f]{6}',x) for x in pal),k)
  for k,edges in d['edges'].items():
   if k in d['palettes']:self.assertEqual(len(edges),len(d['palettes'][k]),k)
  self.assertIn('numericLabels(id,colors)',self.js)
 def test_dropdown_paints_wide_real_bar_and_numbers_separately(self):
  self.assertEqual(len(self.dom.select('.ms-colorbar-picker .ms-gradient-scale')),1)
  self.assertEqual(len(self.dom.select('.ms-colorbar-picker #msPaletteNumericLabels')),1)
  self.assertEqual(len(self.dom.select('#msPaletteOptions[hidden]')),1)
  self.assertIn("$('msPaletteOptions').hidden=true",self.js)
  self.assertIn('const group=groupForParam(',self.js)
  self.assertIn("paletteId=null",self.js)
 def test_safe_sound(self):
  self.assertIsNotNone(self.dom.select_one('#msSoundToggle[aria-pressed="true"]'))
  self.assertIn('audioCtx.createOscillator()',self.js)
  self.assertIn('if(!soundEnabled)return',self.js)
  self.assertNotIn('fetch(',self.js)
  self.assertNotIn('eval(',self.js)
  self.assertNotIn('setInterval(',self.js)
 def test_self_hosted_no_external_asset_and_strict_server(self):
  h=self.dom
  for x in h.select('script[src],link[rel=stylesheet]'):
   src=x.get('src',x.get('href'))
   self.assertIn(src,{'theme.css','vnext2.css','home-atmosphere.css','app.js','palette-data.js','vnext2.js'})
  server=(BASE/'preview_server.py').read_text()
  self.assertIn("'/home-atmosphere.css'",server)
  self.assertIn("self.send_error(404",server)
  self.assertLess((BASE/'home-atmosphere.css').stat().st_size,100_000)
 def test_js_and_css_syntax(self):
  for name in ('app.js','vnext2.js','palette-data.js'):
   p=subprocess.run(['node','--check',str(BASE/name)],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr)
  for name in ('theme.css','vnext2.css','home-atmosphere.css'):
   bad=[x for x in tinycss2.parse_stylesheet((BASE/name).read_text(),skip_whitespace=True,skip_comments=True) if x.type=='error']
   self.assertFalse(bad,f'{name} {bad}')
 def test_both_landscape_and_portrait_keep_desktop_frame(self):
  self.assertIn('min-width:1180px',self.css)
  self.assertNotIn('.ms-workspace{grid-template-columns:1fr',self.css)
  self.assertIn('prefers-reduced-motion:reduce',self.css)
 def test_export_theme_only_decorative(self):
  imagecss=(BASE/'home-atmosphere.css').read_text()
  self.assertIn('data:image/webp;base64,',imagecss)
  self.assertIn('not part of scientific maps',imagecss)
if __name__=='__main__':unittest.main()