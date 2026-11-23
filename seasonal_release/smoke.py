"""Exercise the patched public route using production assets and a local overlay."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent/'dist'
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    page.set_default_timeout(120000)
    loaded = []
    def overlay(route):
        from urllib.parse import urlparse
        path = urlparse(route.request.url).path.lstrip('/') or 'index.html'
        if path == 'version.json':
            route.abort(); return
        local = ROOT/path
        if local.is_file():
            content_type = 'application/javascript' if path.endswith('.js') else 'text/html'
            route.fulfill(body=local.read_bytes(),content_type=content_type)
        else:
            loaded.append(path)
            route.continue_()
    page.route('https://wtafkik.ir/**',overlay)
    page.goto('https://wtafkik.ir/index.html',wait_until='domcontentloaded')
    page.wait_for_function("typeof openSF === 'function' && typeof sfOpenPublished === 'function'")
    # Simulate unavailable publication. The standard route must not start training.
    page.route('**/gallery_latest.json',lambda route:route.fulfill(status=404,body='{}'))
    page.evaluate('openSF()')
    assert page.locator('[data-sfc-published]').is_visible()
    assert page.locator('#sfMain img').is_hidden()
    assert page.evaluate('SF.ready') is False
    assert not any('atlas_pack' in p or 'era5_iran' in p for p in loaded)
    assert page.evaluate("typeof sfRunCustom === 'function' && typeof openON === 'function'")
    browser.close()
print('PASS patched index boots and public seasonal route avoids model loading on publication failure')
