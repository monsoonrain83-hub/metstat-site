"""Deterministic browser contract tests; synthetic DOM, no live NWP data."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
script=(root/'assets/metstat_r5_stage19_controls.js').read_text()
results=[]
html='''<!doctype html><html lang="fa"><head></head><body><main id="onApp"><section class="nvCard">
<canvas id="nvLg" width="600" height="44"></canvas>
<details class="nvCbDd"><summary>رنگ‌بندی</summary><div><button data-cb="def">Default</button></div></details>
<details class="nvLayDd"><summary>لایه‌ها</summary><div>layer toggles</div></details>
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
        ids: [...document.querySelectorAll('[id]')].map(x=>x.id)
      })''')
      assert initial['palette'] and initial['iconCount']==1,initial
      assert initial['border']==('Country and province' if lang=='en' else 'مرز کشور و استان'),initial
      page.locator('#nvLg').click()
      assert page.locator('.nvCbDd').get_attribute('open') is not None
      page.locator('#nvLg').focus()
      page.keyboard.press('Enter')
      assert page.locator('.nvCbDd').get_attribute('open') is None
      page.locator('#nvLg').focus()
      page.keyboard.press('Space')
      assert page.locator('.nvCbDd').get_attribute('open') is not None
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
      assert page.locator('#nvLg[data-ms-r5-palette]').count()==1
      assert len(initial['ids'])==len(set(initial['ids']))
      results.append({'width':w,'height':h,'language':lang,'palette_click_keyboard':'pass',
                      'layer_icon_count':1,'boundary_i18n':'pass','dom_rebuild':'pass'})
      page.close()
  browser.close()
report={'scope':'synthetic DOM only; NOT production or real weather maps','cases':results,'pass':len(results)}
(root/'tests/stage19_test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'pass':len(results),'checked_viewports':4,'languages':2,'scope':report['scope']},ensure_ascii=False))