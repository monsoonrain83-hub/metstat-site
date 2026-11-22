"""Source-grounded r5 UI safety and hierarchical route tests, no external access."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import json,subprocess,threading,unittest,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[1]
ROUTES=json.loads((ROOT/'route_catalog.json').read_text(encoding='utf8'))
GROUPS={
 'پایش و پیش‌بینی':['مدل‌های هواشناسی','متئوگرام','تصویر ماهواره و رادار','شاخص‌های اقلیمی','پیش‌بینی ماهانه و فصلی','شاخص خطر سیل ناگهانی','رصد لحظه‌ای ایستگاه‌ها','تهیه نقشه‌های همبارش از داده‌های ایستگاهی'],
 'هواشناسی کاربردی':['وضعیت کلی','گزارش چندمدلی','هواشناسی کوهستان','گردشگری و سفر','هایکینگ و طبیعت‌گردی','هشدار ۷۲ ساعته','کیفیت هوا و گردوغبار','زلزله‌های اخیر'],
 'تحلیل همدیدی':['تحلیل سینرژی'],
 'هسته تحلیل اقلیم':['اطلس اقلیمی','کارگاه تغییر اقلیم و خشکسالی','اقلیم‌نما','بارش شبکه‌ای GPCC'],
 'ترکیب نقشه‌های آفلاین و آنلاین':['ترکیب خودکار','تحلیل چندمدلی','هشدار جوی','همرفت','اصلاح با ارتفاع','weather.us','WeatherBELL','WeatherModels','TropicalTidbits','سایر وب‌سایت‌های نقشه','تراکم رعدوبرق'],
 'جعبه ابزار هواشناسی':['تبدیل واحدهای هواشناسی','مبدل فایل‌های هواشناسی','مبدل فایل‌های تصویری و ویدئویی','مبدل فایل‌های اسنادی'],
 'استودیو آوا':['تهیه گزارش صوتی هواشناسی از روی متن','ویرایش ویدئو','ویرایش عکس','تشخیص رعدوبرق و تهیه عکس رعدوبرق از روی ویدئو']
}
class HierarchyTests(unittest.TestCase):
 def test_unique_review_paths(self):
  self.assertEqual(len(ROUTES),68)
  self.assertEqual(len(set(x['path'] for x in ROUTES)),68)
  self.assertTrue(all(x['route_verified_live'] is False for x in ROUTES))
 def test_seven_exact_authoritative_top_groups(self):
  roots={p['group']:p for p in ROUTES if p['parent_path'] is None and p['path']!='/' and p['group']!='حساب کاربری'}
  self.assertEqual(set(roots),set(GROUPS))
  for name,titles in GROUPS.items():
   got=[p['title'] for p in ROUTES if p['parent_path']==roots[name]['path']]
   self.assertEqual(got,titles,name)
 def test_climate_workshop_third_level(self):
  p=next(x for x in ROUTES if x['title']=='کارگاه تغییر اقلیم و خشکسالی')
  children=[x['title'] for x in ROUTES if x['parent_path']==p['path']]
  self.assertEqual(children,['تحلیل ایستگاهی','وضعیت منطقه‌ای','تغییر اقلیم مشاهده‌ای','پیش‌نگری آینده CMIP6','تیلور و هدف CMIP6','شاخص‌های اقلیمی xclim','تحلیل موجک'])
 def test_forecast_periods_and_custom_nested(self):
  p='/monitoring-forecast/weather-models'
  self.assertEqual([x['kind'] for x in ROUTES if x['parent_path']==p],['forecast']*5+['custom'])
 def test_parent_paths_are_defined(self):
  paths={x['path'] for x in ROUTES}
  self.assertTrue(all(x['parent_path'] in paths for x in ROUTES if x['parent_path']))
 def test_browser_menu_bug_was_fixed(self):
  js=(ROOT/'app.js').read_text()
  self.assertIn('appendChildren(drop,root.path,0)',js)
  self.assertNotIn("addLevel(drop,'',0)",js)
  self.assertIn('document.body.appendChild(drop)',js)
  self.assertIn('aria-controls',js)
 def test_sound_enabled_and_click_feedback(self):
  js=(ROOT/'app.js').read_text();css=(ROOT/'styles.css').read_text()
  self.assertIn('zoom:100,sound:true',js)
  self.assertIn("t.classList.add('ms-press-feedback')",js)
  self.assertIn('createOscillator',js)
  self.assertIn('prefers-reduced-motion',css)
 def test_model_images_not_emoji(self):
  js=(ROOT/'app.js').read_text();icons=(ROOT/'model-icons.js').read_text()
  self.assertIn('document.createElement(\'img\')',js)
  self.assertNotIn('🇺🇸',js)
  self.assertIn('data:image/svg+xml;base64,',icons)
  self.assertIn('state.period===\'daily\'',js)
 def test_studio_port_not_claimed_full(self):
  js=(ROOT/'ava-studio-r5.js').read_text()
  self.assertIn('speechSynthesis',js)
  self.assertIn('avaPhotoExport',js)
  self.assertIn('avaScan',js)
  self.assertIn('uncalibrated',js)
  self.assertNotIn('fetch(',js)
  self.assertNotIn('XMLHttpRequest',js)
 def test_offline_file_builds_with_no_external_http(self):
  subprocess.run(['python','build_offline.py'],cwd=ROOT,check=True,capture_output=True)
  p=ROOT/'MetStat_vNext_r5_ALL_PAGES_AVA_STUDIO_INTERACTIVE_OFFLINE.html'
  content=p.read_text()
  self.assertGreater(p.stat().st_size,220000)
  self.assertIn('MetStatRoutes=',content)
  self.assertIn('MetStatModelIcons=',content)
  self.assertNotIn('src="app.js"',content)
  self.assertIn("connect-src 'none'",content)
 def test_all_sources_js_syntax(self):
  for p in ['app.js','route-data.js','palette-data.js','model-icons.js','account-r4.js','drawing-r4.js','feature-r5.js','lightning-web-core.js','ava-studio-r5.js']:
   with self.subTest(p=p): subprocess.run(['node','--check',p],cwd=ROOT,check=True,capture_output=True)
class LocalRouteHttpTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import sys
  sys.path.insert(0,str(ROOT))
  from preview_server import PreviewHandler
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),PreviewHandler)
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base='http://127.0.0.1:'+str(cls.server.server_address[1])
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.thread.join(2);cls.server.server_close()
 def test_all_68_independent_deep_links_return_200(self):
  for route in ROUTES:
   with self.subTest(path=route['path']):
    with urllib.request.urlopen(self.base+route['path'],timeout=4) as resp:
     self.assertEqual(resp.status,200)
     self.assertIn('text/html',resp.headers.get('Content-Type',''))
 def test_static_js_and_image(self):
  for path in ['/app.js','/model-icons.js','/ava-studio-r5.js','/assets/homepage_atmosphere.webp']:
   with urllib.request.urlopen(self.base+path) as resp:self.assertEqual(resp.status,200)
 def test_unknown_and_path_traversal_blocked(self):
  for path in ['/not-a-route','/admin.php','/%2e%2e/.env','/assets/%2e%2e/app.js']:
   with self.subTest(path=path),self.assertRaises(urllib.error.HTTPError) as err:urllib.request.urlopen(self.base+path,timeout=4)
   self.assertEqual(err.exception.code,404)
if __name__=='__main__':unittest.main()