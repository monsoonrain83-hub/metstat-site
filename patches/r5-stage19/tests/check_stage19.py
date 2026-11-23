"""Deterministic browser contract tests; synthetic DOM, no live NWP data."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
script=(root/'assets/metstat_r5_stage19_controls.js').read_text()
results=[]
html='''<!doctype html><html lang="fa"><head></head><body><header class="top-in">
<button class="ms7-main" data-group="monitor"><img alt="" src="data:,x"><span>پایش و پیش‌بینی</span><span class="ms7-arrow">⌄</span></button>
<button class="ms7-main" data-group="applied"><span>هواشناسی کاربردی</span></button>
<button class="ms7-main" data-group="synoptic"><span>تحلیل همدیدی</span></button>
<button class="ms7-main" data-group="climate"><span>هسته تحلیل اقلیم</span></button>
<button class="ms7-main" data-group="composer"><span>نقشه‌های آنلاین و آفلاین</span></button>
<button class="ms7-main" data-group="toolbox"><span>جعبه ابزار هواشناسی</span></button>
<button class="ms7-main" data-group="ava"><span>استودیو آوا</span></button>
</header><section class="ms9-geo-bar">
<label>قاره<select data-ms9-geo="continent"><option value="asia">Asia</option></select></label>
<label>Region<select data-ms9-geo="region"><option value="me">Middle East</option><option value="eu">Europe and North کاسپین</option></select></label>
<label>Country<select data-ms9-geo="country"><option value="">تمام Region</option><option value="iran">Iran</option></select></label>
<label>Province / ایالت<select data-ms9-geo="province"><option value="">تمام Provinces</option></select></label>
<label>County<select data-ms9-geo="county"><option value="" disabled>زوم County هنوز Active نیست</option></select></label>
</section><main id="onApp"><section class="nvCard">
<canvas id="nvLg" width="600" height="44"></canvas>
<details class="nvCbDd"><summary>رنگ‌بندی</summary><div><button data-cb="def">Default</button></div></details>
<details class="nvLayDd"><summary>لایه‌ها</summary><div><label><input type="checkbox" data-nvl="road"> جاده‌ها</label><label><input type="checkbox" data-nvl="riv"> رودخانه‌ها</label></div></details>
<select id="nvBm"><option value="prov">x</option><option value="ctry">x</option><option value="cnty">x</option><option value="none">x</option></select>
</section></main></body></html>'''
with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for w,h in [(390,844),(844,390),(960,720),(1440,900)]:
    for lang in ('fa','en'):
      page=browser.new_page(viewport={'width':w,'height':h})
      page.set_content(html)
      page.evaluate('(lang) => document.documentElement.lang=lang',lang)
      page.add_script_tag(content=script)
      page.wait_for_timeout(100)
      initial=page.evaluate('''() => ({
        palette: !!document.querySelector('#nvLg[data-ms-r5-palette]'),
        iconCount: document.querySelectorAll('.nvLayDd svg[data-ms-r5-layers-icon]').length,
        border: document.querySelector('#nvBm option').textContent,
        status: window.MetStatR5Stage19.palette,
        road: document.querySelector('.nvLayDd [data-nvl="road"]').parentNode.textContent.trim(),
        ids: [...document.querySelectorAll('[id]')].map(x=>x.id)
      })''')
      assert initial['palette'] and initial['iconCount']==1,initial
      assert initial['border']==('Country and province' if lang=='en' else 'مرز کشور و استان'),initial
      assert initial['road']==('Roads' if lang=='en' else 'جاده‌ها'),initial
      headLabels=page.evaluate("[...document.querySelectorAll('.ms7-main')].map(x=>x.querySelector('span:not(.ms7-arrow)').textContent.trim())")
      assert headLabels==(['Monitor & Forecast','Applied Weather','Synoptic','Climate','Online / Offline Maps','Weather Tools','Ava Studio'] if lang=='en' else ['پایش و پیش‌بینی','هواشناسی کاربردی','تحلیل همدیدی','هسته تحلیل اقلیم','نقشه‌های آنلاین و آفلاین','جعبه ابزار هواشناسی','استودیو آوا']),headLabels
      assert page.locator('.ms7-main[data-group="monitor"] img').count()==1
      assert page.locator('.ms7-main[data-group="monitor"] .ms7-arrow').count()==1
      geoNames=page.evaluate("[...document.querySelectorAll('[data-ms9-geo]')].map(x=>x.parentElement.firstChild.nodeValue.trim())")
      assert geoNames==(['قاره','منطقه','کشور','استان / ایالت','شهرستان'] if lang=='fa' else ['Continent','Region','Country','Province / State','County']),geoNames
      geoFirst=page.evaluate("[...document.querySelectorAll('[data-ms9-geo]')].map(x=>x.options[0].textContent.trim())")
      assert geoFirst[3]==('همه استان‌ها' if lang=='fa' else 'All provinces'),geoFirst
      assert geoFirst[4]==('زوم شهرستان هنوز فعال نیست' if lang=='fa' else 'County zoom is not active'),geoFirst
      page.locator('#nvLg').click()
      assert page.locator('.nvCbDd').get_attribute('open') is not None
      page.locator('#nvLg').focus()
      page.keyboard.press('Enter')
      assert page.locator('.nvCbDd').get_attribute('open') is None
      page.locator('#nvLg').focus()
      page.keyboard.press('Space')
      assert page.locator('.nvCbDd').get_attribute('open') is not None
      # R5 Stage18 owns the palette click when this native ARIA target exists.
      page.evaluate("""() => {const el=document.querySelector('#nvLg');el.setAttribute('aria-controls','msR5ColorChoices');el.replaceWith(el.cloneNode(true));}""")
      page.wait_for_timeout(100)
      assert page.evaluate('window.MetStatR5Stage19.palette')=='native_picker_preserved'
      # Trigger a subtree replacement and verify idempotent mounting.
      page.evaluate('''() => {
        const original=document.querySelector('.nvCard');
        const next=original.cloneNode(true);
        next.querySelector('#nvLg').removeAttribute('data-ms-r5-palette-bound');
        next.querySelector('.nvCbDd').removeAttribute('data-ms-r5-palette-bound');
        next.querySelector('.nvLayDd svg')?.remove();
        original.replaceWith(next);
      }''')
      page.wait_for_timeout(100)
      assert page.locator('.nvLayDd svg[data-ms-r5-layers-icon]').count()==1
      assert page.locator('#nvLg[aria-controls="msR5ColorChoices"]').count()==1
      assert len(initial['ids'])==len(set(initial['ids']))
      # Explicit language changes preserve existing button icons and listeners.
      page.evaluate("() => {document.documentElement.lang=document.documentElement.lang==='fa'?'en':'fa';document.dispatchEvent(new Event('langchange'));}")
      page.wait_for_timeout(100)
      opposite=page.locator('.ms7-main[data-group="monitor"] span:not(.ms7-arrow)').text_content().strip()
      assert opposite==('پایش و پیش‌بینی' if lang=='en' else 'Monitor & Forecast'),opposite
      reversedGeo=page.evaluate("document.querySelector('[data-ms9-geo=continent]').parentElement.firstChild.nodeValue.trim()")
      assert reversedGeo==('قاره' if lang=='en' else 'Continent'),reversedGeo
      results.append({'width':w,'height':h,'language':lang,'palette_click_keyboard':'pass',
                      'layer_icon_count':1,'boundary_i18n':'pass','stage18_native_palette_preserved':'pass','dom_rebuild':'pass','header_navigation_i18n':'pass','geography_i18n':'pass'})
      page.close()
  browser.close()
report={'scope':'synthetic DOM only; NOT production or real weather maps','cases':results,'pass':len(results)}
(root/'tests/stage19_test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'pass':len(results),'checked_viewports':4,'languages':2,'scope':report['scope']},ensure_ascii=False))