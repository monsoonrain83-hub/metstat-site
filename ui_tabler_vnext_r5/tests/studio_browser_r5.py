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
import base64
(R/'tests'/'fixture_photo.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+vrmcAAAAASUVORK5CYII='))
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(3000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('about:blank');page.set_content(str(html),wait_until='domcontentloaded');page.add_style_tag(content=css)
 for n,s in js:page.add_script_tag(content=s)
 page.locator('[data-nav-trigger="استودیو آوا"]').click()
 page.locator('[data-nav-panel="استودیو آوا"] a[data-route$="photo-editor"]').click()
 page.locator('#avaPhoto').set_input_files(str(R/'tests'/'fixture_photo.png'))
 page.wait_for_timeout(550)
 assert page.locator('#studioStatus').inner_text().startswith('عکس محلی بارگذاری شد'),page.locator('#studioStatus').inner_text()
 page.locator('#avaBrightness').fill('140');page.locator('#avaContrast').fill('125')
 page.screenshot(path=str(R/'tests'/'r5_photo_loaded.png'))
 with page.expect_download(timeout=4000) as download_info:page.locator('#avaPhotoExport').click()
 d=download_info.value;assert d.suggested_filename.endswith('.png')
 print('photo editor changed pixels and PNG download OK')
 page.locator('[data-nav-trigger="استودیو آوا"]').click();page.locator('[data-nav-panel="استودیو آوا"] a[data-route$="lightning-video-detection"]').click()
 assert page.locator('#avaVideo').count()==1
 page.locator('#avaVideo').set_input_files(str(R/'tests'/'lightning_demo_clip.mp4'))
 page.wait_for_timeout(500)
 assert page.locator('#avaPlayer').evaluate('(v)=>!!v.videoWidth'),'cannot play video'
 page.locator('#avaScan').click()
 page.wait_for_timeout(2500)
 print('lightning status:',page.locator('#studioStatus').inner_text()[:280])
 page.screenshot(path=str(R/'tests'/'r5_lightning_scan.png'))
 assert not errors,errors
 browser.close()