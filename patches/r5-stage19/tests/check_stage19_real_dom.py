#!/usr/bin/env python3
"""Offline full-HTML smoke for Stage18 + Stage19, using set_content.

It validates *existing* header and geo controls, not live map data, routed pages,
actual viewport-fit scripts or network dependencies.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('index',type=Path)
parser.add_argument('--asset',type=Path,default=Path(__file__).resolve().parents[1]/'assets/metstat_r5_stage19_controls.js')
args=parser.parse_args()
html=args.index.read_text(encoding='utf-8')
js=args.asset.read_text(encoding='utf-8')
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width,height in [(390,844),(844,390),(960,720),(1440,900)]:
        for initial_language in ('en','fa'):
            page=browser.new_page(viewport={'width':width,'height':height})
            page.set_content(html,wait_until='domcontentloaded',timeout=25000)
            if page.evaluate('document.documentElement.lang') != initial_language:
                page.locator('#langBtn').click(force=True)
            page.add_script_tag(content=js)
            page.wait_for_timeout(100)
            def snapshot():
                return page.evaluate('''() => ({
                    lang: document.documentElement.lang,
                    groups: [...document.querySelectorAll('.ms7-main[data-group]')].map(x => ({
                        key: x.dataset.group, text: x.querySelector('span:not(.ms7-arrow)')?.textContent.trim(),
                        image: !!x.querySelector('.ms7-ico'), arrow: !!x.querySelector('.ms7-arrow')
                    })),
                    geo: [...document.querySelectorAll('[data-ms9-geo]')].map(x => ({
                        key: x.dataset.ms9Geo, label: x.parentElement.firstChild.nodeValue.trim(),
                        values: [...x.options].map(o=>o.value), texts: [...x.options].map(o=>o.textContent.trim())
                    }))
                })''')
            before=snapshot()
            assert len(before['groups'])==7 and len(before['geo'])==5,before
            if initial_language=='en':
                assert before['groups'][0]['text']=='Monitor & Forecast',before
                assert before['geo'][0]['label']=='Continent',before
                assert before['geo'][3]['label']=='Province / State',before
            else:
                assert before['groups'][0]['text']=='پایش و پیش‌بینی',before
                assert before['geo'][0]['label']=='قاره',before
                assert before['geo'][3]['label']=='استان / ایالت',before
            page.locator('#langBtn').click(force=True)
            page.wait_for_timeout(130)
            after=snapshot()
            assert before['lang'] != after['lang']
            assert [x['key'] for x in before['groups']] == [x['key'] for x in after['groups']]
            assert [x['image'] for x in before['groups']] == [x['image'] for x in after['groups']]
            assert [x['arrow'] for x in before['groups']] == [x['arrow'] for x in after['groups']]
            for a,b in zip(before['geo'],after['geo']):
                assert a['key']==b['key'] and a['values']==b['values'],(a,b)
            results.append({'width':width,'height':height,'initial':initial_language,'header_groups':7,'geo_selectors':5,'locale_roundtrip':'pass','original_options_values':'preserved'})
            page.close()
    browser.close()
report={'scope':'actual Stage18 full HTML loaded offline by browser set_content, no network or real NWP data; NOT viewport-fit/full-route QA', 'cases':results,'pass':len(results)}
path=Path(__file__).with_name('stage19_real_dom_results.json')
path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'pass':len(results),'scope':report['scope']},ensure_ascii=False))