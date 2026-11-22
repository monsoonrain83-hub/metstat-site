from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import base64,json
R=Path(__file__).resolve().parents[1]
html=BeautifulSoup((R/'index.html').read_text(),'html.parser')
for t in html.select('script,link[rel="stylesheet"],meta[http-equiv="Content-Security-Policy"]'):t.decompose()
css=(R/'styles.css').read_text().replace("url('assets/homepage_atmosphere.webp')", "url('data:image/webp;base64,"+base64.b64encode((R/'assets/homepage_atmosphere.webp').read_bytes()).decode('ascii')+"')")
js=[]
for n in ['route-data.js','palette-data.js','model-icons.js','app.js','account-r4.js','drawing-r4.js','feature-r5.js','ava-studio-r5.js']:
 s=(R/n).read_text()
 if n=='app.js':s=s.replace("location.protocol==='file:'", "(location.protocol==='file:'||location.protocol==='about:')")
 js.append((n,s))
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for w,h in [(1440,900),(844,390),(390,844),(1920,1080)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1)
  page=ctx.new_page();page.set_default_timeout(2800);err=[];page.on('pageerror',lambda x:err.append(str(x)))
  page.goto('about:blank');page.set_content(str(html),wait_until='domcontentloaded');page.add_style_tag(content=css)
  for n,s in js:page.add_script_tag(content=s)
  page.wait_for_timeout(200)
  count=page.evaluate('window.MetStatR3Preview?.routeCount');assert count==68,(w,count)
  groups=page.locator('#mainNav [data-nav-trigger]');assert groups.count()==7,(w,groups.count())
  print(w,h,'initial err:',err,'groups',groups.count())
  if w==1440:
   for group,expected in [('پایش و پیش‌بینی','متئوگرام'),('هواشناسی کاربردی','گزارش چندمدلی'),('تحلیل همدیدی','تحلیل سینرژی'),('هسته تحلیل اقلیم','تحلیل موجک'),('ترکیب نقشه‌های آفلاین و آنلاین','همرفت'),('جعبه ابزار هواشناسی','مبدل فایل‌های اسنادی'),('استودیو آوا','ویرایش عکس')]:
    b=page.locator(f'[data-nav-trigger="{group}"]');b.click()
    menu=page.locator(f'[data-nav-panel="{group}"]');assert menu.is_visible(),(group,'menu hidden');assert menu.locator('a').count()>1,(group,'empty menu');
    if group=='هسته تحلیل اقلیم':
     branch=menu.locator('summary',has_text='کارگاه تغییر اقلیم و خشکسالی');branch.click();assert menu.get_by_text('تحلیل موجک').count()>=1
     a=menu.locator('a[data-route$="wavelet-analysis"]');a.click()
    else:
     a=menu.locator('a',has_text=expected).first;a.click()
    route=page.evaluate('window.MetStatR3Preview.getRoute()');title=page.locator('#pageTitle').inner_text()
    assert expected in title,(group,route,title)
    print('nav',group,'=>',route,'title',title)
   page.locator('[data-nav-trigger="استودیو آوا"]').click()
   page.locator('[data-nav-panel="استودیو آوا"] a[data-route$="photo-editor"]').click()
   assert page.locator('#studioR5').is_visible()
   assert page.locator('#avaPhoto').count()==1
   page.screenshot(path=str(R/'tests'/'r5_studio_photo.png'))
   page.locator('[data-nav-trigger="پایش و پیش‌بینی"]').click()
   panel=page.locator('[data-nav-panel="پایش و پیش‌بینی"]');panel.locator('summary',has_text='مدل‌های هواشناسی').click()
   panel.locator('a[data-route="/monitoring-forecast/weather-models"]').click()
   assert page.locator('#mapModelRail .model-asset').count()>=5
   page.screenshot(path=str(R/'tests'/'r5_forecast_models.png'))
   page.locator('#accountToggle').click();assert page.locator('#accountDropdown').is_visible()
   page.locator('#accountDropdown [data-route="/account/admin"]').click();assert page.locator('#accountView').get_attribute('aria-hidden')=='false';page.screenshot(path=str(R/'tests'/'r5_account.png'))
   page.locator('[data-nav-trigger="هسته تحلیل اقلیم"]').click();page.screenshot(path=str(R/'tests'/'r5_climate_dropdown.png'))
  if w==844:
   page.locator('[data-nav-trigger="پایش و پیش‌بینی"]').click();page.screenshot(path=str(R/'tests'/'r5_landscape_nav.png'))
  assert not err,(w,err)
  ctx.close()
 browser.close()
print('BROWSER R5 PASS')