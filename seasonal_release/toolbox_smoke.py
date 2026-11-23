"""Self-contained toolbox checks: no external Google AI Studio access is required."""
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    page.route('https://ai.studio/**', lambda route: route.abort())
    page.goto((root / 'toolbox.html').as_uri(), wait_until='domcontentloaded')
    assert page.title() == 'جعبه ابزار هواشناسی | MetStat'
    assert page.locator('#ava-studio').is_visible()
    assert page.locator('iframe#ava-frame').count() == 1
    source = page.locator('#ava-frame').get_attribute('src')
    assert source.startswith('https://ai.studio/apps/06513bbb-1b5b-499f-86f5-8fe82acc1d88')
    assert page.locator('#ava-open').get_attribute('href') == source
    assert page.locator('a[href="./index.html"]').count() == 1
    page.locator('#ava-reload').click()
    page.route('https://wtafkik.ir/index.html', lambda route: route.fulfill(body='<header><nav id="mainNav"></nav></header>', content_type='text/html'))
    page.goto('https://wtafkik.ir/index.html', wait_until='domcontentloaded')
    page.add_script_tag(path=str(root / 'assets' / 'ava_toolbox_entry.js'))
    page.add_script_tag(path=str(root / 'assets' / 'ava_toolbox_entry.js'))
    assert page.locator('#mainNav > #metstat-weather-toolbox-link').count() == 1
    assert page.locator('#metstat-weather-toolbox-link').get_attribute('href') == 'toolbox.html'
    browser.close()
print('PASS standalone toolbox, AVA source, reload, nav link, duplicate prevention')
