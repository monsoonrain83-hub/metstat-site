from playwright.sync_api import sync_playwright
from pathlib import Path
import re,json
P=Path('/mnt/data/metstat_r88_work'); css=(P/'public/assets/metstat_graphite_shell_v88.css').read_text(); html=(P/'public/index.html').read_text()
loader=re.search(r'function msLoadShow\(\)\{.*?\n\}\nfunction msLoadDone',html,re.S)
if not loader:
 loader=re.search(r'(function msLoadShow\(\)\{.*?\n  e\.__t=setInterval\(.*?\); \})\nfunction msLoadDone',html,re.S)
assert loader
fn=loader.group(1) if loader.lastindex else loader.group(0).rsplit('function msLoadDone',1)[0]
fixture='''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=1360, user-scalable=yes"><style>html,body{margin:0}body{font:14px Tahoma,Arial} .top{min-height:70px;padding:12px 16px;box-sizing:border-box} .wrap{display:grid;padding:8px} .panel,.card{padding:14px;margin-bottom:12px} #nvStage{height:570px;background:linear-gradient(135deg,#e8edf0,#e6e9eb);color:#292b2d;display:flex;align-items:center;justify-content:center;font-size:28px} #nvViewer{max-width:100%} .nvCard{padding:12px;background:#e8e9eb} #onAside details{padding:12px;border-bottom:1px solid #777} .msPg,.msSec{background:blue} .mlBar i{display:block;width:0} </style><style>__CSS__</style></head><body><div class="top"><strong>MetStat | Maps</strong>　　<span>پایش و پیش‌بینی هواشناسی</span></div><nav id="msNav" class="msNav"><div id="msNavR1" class="msNavR1"><button class="msPg on">نقشه‌های هواشناسی</button><button class="msPg">داده‌های ایستگاهی</button><button class="msPg">تحلیل اقلیمی</button><button class="msPg">جعبه ابزار</button><button class="msPg">پایش دقت مدل‌ها</button></div><div id="msNavR2" class="msNavR2"><button class="msSec on">نقشه‌های مدل‌های جهانی</button><button class="msSec">نقشه‌های برآوردی</button><button class="msSec">ماهواره</button><button class="msSec">هم‌بارش</button></div></nav><div id="onApp" class="wrap"><aside id="onAside"><section class="panel"><h3>تنظیمات نقشه</h3><details open><summary>مدل هواشناسی</summary><select><option>GEM GDPS</option><option>ECMWF</option><option>GFS</option></select></details><details open><summary>پارامترها</summary><button>بارش تجمعی</button><button>دمای ۸۵۰</button></details><details><summary>ناحیه و لایه‌ها</summary><button>مرز استان‌ها</button></details></section></aside><main><article class="card"><div class="nvCard" style="background:#eff0f0"><h3 style="color:#292b2d">نقشهٔ پیش‌بینی مدل‌ها</h3><div class="nvStage" id="nvStage">فضای نقشه / نمودار</div></div></article></main></div></body></html>'''.replace('__CSS__',css)
(P/'qa/layout_fixture_r88.html').write_text(fixture)
result=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for lang,width,mobile in [('fa',1440,False),('en',1440,False),('fa',390,True),('en',390,True)]:
  context=browser.new_context(viewport={'width':width,'height':900},is_mobile=mobile,has_touch=mobile,user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Mobile Safari/537.36' if mobile else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36')
  page=context.new_page();page.set_content(fixture,wait_until='domcontentloaded');page.evaluate('''lang => {document.documentElement.lang=lang;document.documentElement.dir=lang==='fa'?'rtl':'ltr';}''',lang)
  geom=page.evaluate('''() => {const b=id=>{const r=document.querySelector(id).getBoundingClientRect();return {x:Math.round(r.x),width:Math.round(r.width),top:Math.round(r.top),height:Math.round(r.height)}}; return {innerWidth:innerWidth,nav:b('#msNav'),side:b('#onAside'),map:b('#onApp>main'),bodyScroll:document.documentElement.scrollWidth};}''')
  if lang=='fa':assert geom['side']['x']>geom['map']['x']+geom['map']['width']-3,geom
  else:assert geom['side']['x']+geom['side']['width']<geom['map']['x']+3,geom
  assert geom['nav']['top']>=0,geom
  page.screenshot(path=str(P/f'qa/graphite_{lang}_{width}.png'),full_page=True)
  result.append({'locale':lang,'device_width':width,'mobile':mobile,**geom})
  page.close();context.close()
 for mobile in (False,True):
  ctx=browser.new_context(viewport={'width':390 if mobile else 1440,'height':780},is_mobile=mobile,has_touch=mobile,user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Mobile Safari/537.36' if mobile else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36')
  pg=ctx.new_page();pg.set_content(fixture);pg.evaluate('() => { '+fn+'; msLoadShow(); }')
  found=pg.locator('#msMobileRotateHint').count();assert found==(1 if mobile else 0),(mobile,found)
  if mobile:
   assert pg.locator('#msMobileRotateHint').inner_text()=='برای تجربه بهتر در موبایل، گوشی رو بچرخونید و در حالت افقی از سایت استفاده کنید.'
   pg.screenshot(path=str(P/'qa/mobile_loader_390.png'))
   pg.evaluate("() => { document.documentElement.lang='en'; "+fn+"; msLoadShow(); }")
   assert 'rotate your phone' in pg.locator('#msMobileRotateHint').inner_text()
  result.append({'loader_mobile':mobile,'hint_present':bool(found)})
  pg.close();ctx.close()
 browser.close()
(P/'qa/browser_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
