"""Real Chromium DOM checks via about:blank document injection.
Managed URLBlocklist blocks local URLs; test runs without any network request.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json,base64,sys
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text(encoding='utf8')
s=BeautifulSoup(html,'html.parser')
for n in s.select('script,link[rel=stylesheet],meta[http-equiv="Content-Security-Policy"]'):n.decompose()
css=(root/'styles.css').read_text(encoding='utf8').replace("url('assets/homepage_atmosphere.webp')",f"url('data:image/webp;base64,{base64.b64encode((root/'assets/homepage_atmosphere.webp').read_bytes()).decode()}')")
scripts=[(root/n).read_text(encoding='utf8') for n in ['route-data.js','palette-data.js','app.js']]
scripts[-1]=scripts[-1].replace("location.protocol==='file:'","(location.protocol==='file:'||location.protocol==='about:')")
routes=json.loads((root/'route_catalog.json').read_text(encoding='utf8'))
issues=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':900})
 page.on('pageerror',lambda e:issues.append('JS error: '+str(e)))
 page.goto('about:blank')
 page.set_content(str(s))
 page.add_style_tag(content=css)
 for t in scripts:page.add_script_tag(content=t)
 # Navigate through all 43 routes through the same event delegation users click.
 for r in routes:
  path=r['path']
  resp=page.evaluate('''p=>{
   const a=document.querySelector('[data-route="'+p+'"]');
   if(!a)return 'missing link';
   a.click();return window.MetStatR3Preview.getRoute();
  }''',path)
  if resp!=path:issues.append(f'route mismatch {path} => {resp}')
  title=page.locator('#pageTitle').inner_text()
  if title!=r['title']:issues.append(f'title mismatch {path}: {title}')
  if not page.locator('#sidebarContent').inner_text().strip():issues.append('no sidebar '+path)
  if r['kind']=='custom' and page.evaluate('window.MetStatR3Preview.getMode()')!='custom':issues.append('no custom panel')
 # Forecast period names and rail flag/text behavior
 page.evaluate('document.querySelector("[data-route=\\"/monitoring-forecast/weather-models/daily\\"]").click()')
 daily=page.locator('.model-status .model-face').all_inner_texts()
 if len(daily)<5 or '🇨🇦' not in daily:issues.append('daily status icons incorrect '+str(daily))
 page.evaluate('document.querySelector("[data-route=\\"/monitoring-forecast/weather-models/monthly\\"]").click()')
 monthly=page.locator('.model-status .model-face').all_inner_texts()
 if 'SEAS5' not in monthly or 'NMME' not in monthly:issues.append('monthly model IDs incorrect '+str(monthly))
 page.locator('#customShortcut').click()
 if page.evaluate('window.MetStatR3Preview.getMode()')!='custom':issues.append('multimodel switch failed')
 page.locator('#generateCustom').click()
 if page.evaluate('window.MetStatR3Preview.getCustom().generated')!=True:issues.append('multimodel generation preview failed')
 page.locator('#forecastTab').click()
 if page.evaluate('window.MetStatR3Preview.getMode()')!='forecast':issues.append('multimodel restore failed')
 # Layer control, palette swatch, touch zoom/pinch settings, icon-only map actions.
 page.locator('#layersBtn').click()
 if not page.locator('#layersPanel').is_visible():issues.append('layers did not open')
 page.locator('#layersClose').click()
 page.locator('#paletteBtn').click()
 if not page.locator('#paletteChoices').is_visible():issues.append('palette did not open')
 palette_entries=page.locator('[data-palette-choice]').count()
 if palette_entries<1:issues.append('palette list too short')
 page.locator('[data-palette-choice]:not([disabled])').first.click()
 if not page.locator('#paletteChoices').is_hidden():issues.append('palette did not close')
 print('ROUTE COUNT',len(routes),'MONTHLY MODEL LABELS',monthly,'PALETTE CHOICES',palette_entries)
 # Overlap checks of fixed rails vs save in all three shape configurations.
 for dims in [(1440,900),(844,390),(390,844)]:
  page.set_viewport_size({'width':dims[0],'height':dims[1]})
  page.wait_for_timeout(60)
  rects=page.evaluate('''() => {
   const r=id=>{const x=document.getElementById(id).getBoundingClientRect();return {left:x.left,top:x.top,right:x.right,bottom:x.bottom,w:x.width,h:x.height}}
   return {map:r('mapStage'),save:r('saveBtn'),palette:r('mapPalette'),left:r('mapLeftRail'),right:r('mapModelRail'),app:r('app'),card:r('mapCard')};
  }''')
  def clash(a,b):return max(a['left'],b['left']) < min(a['right'],b['right'])-1 and max(a['top'],b['top']) < min(a['bottom'],b['bottom'])-1
  for a,bid in [('save','palette'),('save','left'),('save','right'),('palette','right')]:
   if clash(rects[a],rects[bid]):issues.append(f'overlap {dims} {a} {bid}')
  if rects['app']['h']>dims[1]+1:issues.append(f'vertical app overflow {dims} {rects["app"]}')
  print('VIEW',dims,'app-height',rects['app']['h'],'stage-height',rects['map']['h'])
 # Fullscreen should not duplicate map, controls or vertical status buttons.
 page.set_viewport_size({'width':1440,'height':900})
 page.locator('#fullscreenBtn').click()
 if page.locator('.map-card').count()!=1:issues.append('fullscreen duplicated map')
 if page.locator('.model-status').count()!=len(monthly):issues.append('fullscreen duplicated model buttons')
 page.keyboard.press('Escape')
 b.close()
print('RESULT: issues=',len(issues))
if issues:
 print('\n'.join(issues))
 sys.exit(1)