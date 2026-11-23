"""Offline/browser structure regression for MetStat r85. Run only against your own local index.
Requires: lxml, playwright, node, Chromium.
"""
import argparse, json, subprocess, tempfile, shutil
from pathlib import Path
from collections import Counter
from lxml import html
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser()
ap.add_argument('index',help='Patched index_r85.html')
ap.add_argument('--browser',default='/usr/bin/chromium')
a=ap.parse_args()
p=Path(a.index);text=p.read_text(encoding='utf-8');root=html.fromstring(text)
ids=[e.get('id') for e in root.xpath('//*[@id]')];duplicate=[k for k,v in Counter(ids).items() if v>1]
assert not duplicate,f'Duplicate ids: {duplicate[:20]}'
with tempfile.TemporaryDirectory() as tmp:
 js=[]
 for i,e in enumerate(root.xpath('//script[not(@src)]')):
  path=Path(tmp)/f'{i}.js';path.write_text(e.text or '',encoding='utf-8')
  r=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
  assert r.returncode==0,r.stderr
  js.append(i)

stub='<script>window.I18N_D={};window.SITE_URL="wtafkik.ir";window.LOGO_SRC="";window.BORDERS={};window.UBD={};window.TERRAIN_B64="";window.TERRAIN_META={nx:0,ny:0};</script>'
assert '<head>' in text
text=text.replace('<head>','<head>'+stub,1)
results=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(headless=True,executable_path=a.browser,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in [360,390,650,768,1024,1366]:
  page=b.new_page(viewport={'width':width,'height':850})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(text,wait_until='domcontentloaded',timeout=45000)
  page.wait_for_timeout(1000)
  row=page.evaluate('''()=>({innerWidth,scrollWidth:document.documentElement.scrollWidth,nav:document.querySelectorAll('#msNavR1 button').length,meta:document.querySelector('meta[name=viewport]').content})''')
  assert row['scrollWidth']<=width,f'Overflow at {width}: {row}'
  assert not errors,errors[:4]
  assert row['nav']==6,row
  results.append({'viewport':width,'result':row})
  page.close()
 b.close()
print(json.dumps({'status':'PASS','inline_js':len(js),'duplicate_ids':len(duplicate),'browser_cases':len(results),'results':results},ensure_ascii=False,indent=2))
