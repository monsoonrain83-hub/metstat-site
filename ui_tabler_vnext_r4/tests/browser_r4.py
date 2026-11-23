from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import base64,traceback,json,sys
R=Path(__file__).resolve().parents[1]
html=BeautifulSoup((R/'index.html').read_text(),'html.parser')
for el in html.select('script,link[rel="stylesheet"],meta[http-equiv="Content-Security-Policy"]'):el.decompose()
css=(R/'styles.css').read_text().replace("url('assets/homepage_atmosphere.webp')", "url('data:image/webp;base64,"+base64.b64encode((R/'assets/homepage_atmosphere.webp').read_bytes()).decode('ascii')+"')")
js=[]
for n in ['route-data.js','palette-data.js','app.js','account-r4.js','drawing-r4.js']:
 s=(R/n).read_text()
 if n=='app.js':s=s.replace("location.protocol==='file:'","(location.protocol==='file:'||location.protocol==='about:')")
 js.append((n,s))
errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for w,h in [(1920,1080),(1440,900),(1280,720),(844,390),(390,844)]:
  ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1)
  page=ctx.new_page();page.set_default_timeout(1800);e=[];page.on('pageerror',lambda ex:e.append(str(ex)))
  try:
   page.goto('about:blank');page.set_content(str(html),wait_until='domcontentloaded');page.add_style_tag(content=css)
   for n,s in js:page.add_script_tag(content=s)
   page.wait_for_timeout(150)
   count=page.evaluate('window.MetStatR3Preview?.routeCount')
   assert count==63,(w,count)
   assert page.locator('#mainNav .nav-group').count()==6,(w,'nav')
   assert page.locator('#accountToggle').count()==1
   assert page.locator('#drawingOverlay').count()==1
   assert not e,(w,e)
   # Screenshot main UI; source rendering on about:blank is only offline preview.
   page.screenshot(path=str(R/'tests'/f'r4_{w}x{h}.png'))
   if w==1440:
    page.locator('#accountToggle').click();assert page.locator('#accountDropdown').is_visible()
    assert page.locator('.account-menu-link').count()>=6
    page.locator('[data-route="/account"]').last.click()
    assert page.evaluate('window.MetStatR3Preview.getMode()')=='account'
    print('ACCOUNT_STYLE', page.evaluate("() => {const a=document.querySelector('#accountView'), p=a.parentElement, c=a.querySelector('.account-workspace'); const r=a.getBoundingClientRect(); const el=document.elementFromPoint(r.left+300,r.top+160);return {acc:getComputedStyle(a).background,accZ:getComputedStyle(a).zIndex,accVis:getComputedStyle(a).visibility,accOpacity:getComputedStyle(a).opacity,parent:getComputedStyle(p).background,stack:el?.outerHTML?.slice(0,200),parentTop:a.parentNode.lastElementChild?.id}}"),flush=True); page.screenshot(path=str(R/'tests'/'r4_account_1440.png'))
    page.locator('[data-account-action="admin-demo"]').last.click();assert page.evaluate('window.MetStatR4Account.getRole()')=='admin'
    # Use internal route action via clicking menu entry instead of arbitrary eval in production.
    page.locator('#accountToggle').click();page.locator('[data-route="/account/station-approval"]').last.click()
    assert page.evaluate('window.MetStatR3Preview.getRoute()')=='/account/station-approval'
    page.locator('#accountToggle').click();page.locator('[data-route="/account"]').last.click()
    page.locator('#mainNav [data-nav-trigger="پایش و پیش‌بینی"]').click()
    section=page.locator('#mainNav [data-nav-panel="پایش و پیش‌بینی"]')
    print('before summary',page.evaluate("() => {const d=document.querySelector('[data-nav-panel=\"پایش و پیش‌بینی\"]');let r=d.getBoundingClientRect();return {hidden:d.hidden,rect:[r.x,r.y,r.width,r.height],vis:getComputedStyle(d).visibility,css:getComputedStyle(d).display,svg:document.querySelector('[data-nav-trigger=\"پایش و پیش‌بینی\"]').getAttribute('aria-expanded')}}"),flush=True)
    page.wait_for_timeout(220)
    page.screenshot(path=str(R/'tests'/'r4_nav_open.png'))
    section.locator('summary').filter(has_text='پایش و پیش‌بینی').first.click()
    section.locator('summary').filter(has_text='مدل‌های هواشناسی').click()
    section.locator('[data-route="/monitoring-forecast/weather-models"]').click()
    assert page.evaluate('window.MetStatR3Preview.getMode()')=='forecast'
    page.locator('#drawingToggle').click();assert page.locator('#drawingTools').is_visible()
    page.locator('[data-draw="cold"]').click()
    page.locator('#drawingClose').click()
    stage=page.locator('#drawingOverlay').bounding_box();assert stage
    start=(stage['x']+stage['width']*.30,stage['y']+stage['height']*.45)
    print('DRAW_PRE',page.evaluate('''([x,y])=>{let o=document.querySelector('#drawingOverlay'),h=o.querySelector('[data-draw-capture]'),e=document.elementFromPoint(x,y);return {tool:window.MetStatR4Drawing.getTool(),active:o.dataset.active,pe:getComputedStyle(o).pointerEvents,rect:o.getBoundingClientRect().toJSON(),hit:h?.getBoundingClientRect().toJSON(),target:e?.outerHTML?.slice(0,150),map:document.querySelector('#app').dataset.mode}}''',list(start)),flush=True)
    end=(stage['x']+stage['width']*.65,stage['y']+stage['height']*.56)
    page.mouse.move(*start);page.mouse.down()
    for j in range(1,12):page.mouse.move(start[0]+(end[0]-start[0])*j/11,start[1]+(end[1]-start[1])*j/11)
    page.mouse.up();page.wait_for_timeout(70)
    cnt=page.evaluate('window.MetStatR4Drawing.getCount()')
    assert cnt==1,('draw failed',cnt)
    assert page.locator('#drawingOverlay [data-draw-shape="cold"]').count()==1
    page.screenshot(path=str(R/'tests'/'r4_drawing_1440.png'))
    page.locator('#drawingToggle').click()
    page.locator('#drawUndo').click();assert page.evaluate('window.MetStatR4Drawing.getCount()')==0
    page.locator('#drawRedo').click();assert page.evaluate('window.MetStatR4Drawing.getCount()')==1
    page.locator('[data-draw="text"]').click()
    page.locator('#drawingClose').click()
    page.mouse.click(start[0]+40,start[1]+90)
    assert page.locator('#drawTextDialog').evaluate('(e)=>e.open')
    page.locator('#drawTextInput').fill('آزمون نمایشی')
    page.locator('#drawTextConfirm').click()
    assert page.evaluate('window.MetStatR4Drawing.getCount()')==2
    page.screenshot(path=str(R/'tests'/'r4_text_1440.png'))
    page.locator('#fullscreenBtn').click();page.wait_for_timeout(80)
    assert page.locator('#mapCard').is_visible()
    page.screenshot(path=str(R/'tests'/'r4_fullscreen_1440.png'))
   if w==844:
    page.locator('#drawingToggle').click();
    tr=page.locator('#drawingTools').bounding_box();st=page.locator('#mapStage').bounding_box()
    assert tr and tr['width']<=st['width']+10,(w,tr,st)
    page.screenshot(path=str(R/'tests'/'r4_drawing_844x390.png'))
   if w==390:
    assert page.evaluate('document.querySelector(".app").getBoundingClientRect().width')>=960
  except Exception as ex:
   print('FAILED',w,h,str(ex)[:240],flush=True)
   errors.append({'viewport':(w,h),'error':str(ex),'trace':traceback.format_exc()[-1000:],'page_errors':e})
  print('VIEW',w,h,'errors',len(e),'routes',page.evaluate('window.MetStatR3Preview?.routeCount'),flush=True)
  page.close();ctx.close()
 b.close()
print('ISSUES',json.dumps(errors,ensure_ascii=False,indent=2))
if errors:sys.exit(1)