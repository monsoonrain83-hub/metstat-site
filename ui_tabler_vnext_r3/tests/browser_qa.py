from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import base64,json,re,sys
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text(encoding='utf8')
soup=BeautifulSoup(html,'html.parser')
for x in soup.select('script,link[rel="stylesheet"],meta[http-equiv="Content-Security-Policy"]'): x.decompose()
# remove external image because file:// and localhost URLs are blocked by managed Chromium
css=(root/'styles.css').read_text(encoding='utf8')
raw=(root/'assets/homepage_atmosphere.webp').read_bytes()
css=css.replace("url('assets/homepage_atmosphere.webp')",f"url('data:image/webp;base64,{base64.b64encode(raw).decode()}')")
srcs=[(root/n).read_text(encoding='utf8') for n in ['route-data.js','palette-data.js','app.js']]
# Browser policy blocks file:// and localhost navigations; testing is on about:blank.
# Treat about:blank like offline file during injection ONLY. Production source is unchanged.
srcs[-1]=srcs[-1].replace("location.protocol==='file:'","(location.protocol==='file:'||location.protocol==='about:')")
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 issues=[]
 for width,height in [(1920,1080),(1440,900),(1280,720),(844,390),(390,844)]:
  page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda err:errors.append(str(err)))
  try:
   page.goto('about:blank')
   page.set_content(str(soup),wait_until='domcontentloaded',timeout=10000)
   page.add_style_tag(content=css)
   for script in srcs:page.add_script_tag(content=script)
   page.wait_for_timeout(300)
   info=page.evaluate('''() => {
    const ids=['header','sidebar','mapCard','mapStage','mapLeftRail','mapModelRail','mapPalette','mapPalette'];
    const b=Object.fromEntries(ids.map(id=>{const r=document.getElementById(id).getBoundingClientRect();return [id,{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}]}));
    return {path:window.MetStatR3Preview?.getRoute(),count:window.MetStatR3Preview?.routeCount,appw:document.getElementById('app').getBoundingClientRect().width,viewport:{width:innerWidth,height:innerHeight},bounds:b};
   }''')
   print('SCREEN',width,height, 'route',info['path'],'count',info['count'],'appW',info['appw'],'errors',errors[:3])
   if info['count']!=43 or errors:issues.append({'viewport':(width,height),'errors':errors,'info':info})
   if width>=960:
    if info['bounds']['mapCard']['bottom']>height+2 or info['bounds']['sidebar']['bottom']>height+2:issues.append({'viewport':(width,height),'bounds-bottom':info['bounds']})
   page.screenshot(path=str(root/'tests'/f'preview_{width}x{height}.png'),full_page=False)
   if width==1440:
    # Test model rail compact and UI state changes in actual Chromium DOM.
    page.locator('#customShortcut').click()
    page.wait_for_timeout(180)
    print('MULTI:',page.evaluate('window.MetStatR3Preview.getMode()'),'visible custom',page.locator('#customView').get_attribute('aria-hidden'))
    page.screenshot(path=str(root/'tests'/'preview_1440_custom.png'))
    page.locator('#generateCustom').click()
    print('CUSTOM generated?',page.evaluate('window.MetStatR3Preview.getCustom().generated'))
    page.locator('#forecastTab').click()
    print('BACK:',page.evaluate('window.MetStatR3Preview.getMode()'),'route',page.evaluate('window.MetStatR3Preview.getRoute()'))
    page.locator('#saveBtn').click()
    print('SAVE DIALOG',page.locator('#exportDialog').evaluate('(x)=>x.open'))
    page.locator('#openGif').click()
    print('GIF DIALOG',page.locator('#gifDialog').evaluate('(x)=>x.open'))
    page.keyboard.press('Escape')
    page.locator('#layersBtn').click()
    print('LAYERS',page.locator('#layersPanel').is_visible())
    page.locator('#layersClose').click()
    page.locator('[data-nav-trigger="جعبه ابزار هواشناسی"]').click()
    page.locator('[data-route="/meteorological-tools/rainfall-isohyet"]').first.click()
    print('OTHER PAGE:',page.evaluate('window.MetStatR3Preview.getRoute()'),'current controls',page.locator('#sidebarContent select').count())
    page.screenshot(path=str(root/'tests'/'preview_1440_isohyet.png'))
  except Exception as e:
   print('QA ERROR',width,height,str(e)[:700]);issues.append({'viewport':(width,height),'error':str(e)})
  finally:page.close()
 b.close()
 print('QA ISSUES',len(issues))
 if issues:
  (root/'tests'/'browser_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2))
  sys.exit(1)