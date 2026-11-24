#!/usr/bin/env python3
"""Create Stage29 from the EXACT Stage28 R5 staged archive; no host writes.

The ZIP is a staging artifact, never the active cPanel release.
"""
import argparse
import hashlib
import zipfile
from pathlib import Path

EXPECTED_STAGE28 = "a7646948ebd22e0b7d5b794ff6ff419a9d79873e085145322888b9b8e4be0f83"
OLD = ("assets/metstat_original_model_chips_horizontal.js",
       "assets/metstat_original_model_chips_horizontal.css")
TARGET = "assets/metstat_r5_stage24_restore.js"
REFS = (
    '<script src="assets/metstat_original_model_chips_horizontal.js?v=20261121"></script>',
    '<link rel="stylesheet" href="assets/metstat_original_model_chips_horizontal.css?v=20261121">',
)


def single_replace(src, needle, replacement):
    if src.count(needle) != 1:
        raise RuntimeError("Stage28 source marker changed: " + needle[:110])
    return src.replace(needle, replacement, 1)


def rebuild(source: Path, output: Path):
    with zipfile.ZipFile(source) as z:
        files = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
    basehash = hashlib.sha256(files["index.html"]).hexdigest()
    if basehash != EXPECTED_STAGE28:
        raise RuntimeError("Unexpected Stage28 index; do not overwrite a newer site")
    html = files["index.html"].decode("utf-8")
    for ref in REFS:
        html = single_replace(html, ref, "")
    for name in OLD:
        files.pop(name)
    if html.count("function nativeFullscreenDock()") != 1:
        raise RuntimeError("Existing R7 fullscreen controller is not unique")
    if html.count("document.addEventListener('metstat:nvf-enter',nativeFullscreenDock)") != 1:
        raise RuntimeError("Native fullscreen lifecycle listener missing")
    files["index.html"] = html.encode("utf-8")

    js = files[TARGET].decode("utf-8")
    helpers = """
 const ARCHIVE_EN={"isohyet":"Station rainfall / isohyet maps","toolbox-full":"Meteorological toolbox","verify-forecast":"Forecast verification","bulletin-maps":"Bulletin weather maps","convert-unit":"Meteorological unit conversion","toolbox-spatial":"Station precipitation IDW"};
 const liveEnglish=()=>((typeof LANG!=='undefined'&&LANG==='en')||document.documentElement.lang.toLowerCase().startsWith('en'));
 const message=(name)=>({
  loading:['در حال بررسی نسخه اصلی ماژول…','Checking the verified module…'],
  failed:['این ماژول در فایل‌های نصب‌شده پیدا نشد یا با نسخه بررسی‌شده مطابقت ندارد. برای جلوگیری از نمایش نسخه اشتباه باز نشد.','The module is missing or its revision does not match the verified version. Loading was blocked.'],
  gis:['مرزهای نقشه همبارش با نسخه تأییدشده مطابقت ندارند؛ ماژول برای جلوگیری از نمایش نقشه نادرست متوقف شد.','Isohyet boundary data failed integrity verification. The map was stopped.']
 })[name][liveEnglish()?1:0];
"""
    js = single_replace(js, " const MODULES=", helpers+" const MODULES=")
    js = single_replace(js,
        "banner.textContent='در حال بررسی نسخه اصلی ماژول…';",
        "banner.dataset.msArchiveState='loading';banner.textContent=message('loading');")
    js = single_replace(js,
        "error.textContent='مرزهای نقشه همبارش با نسخه تأییدشده مطابقت ندارند؛ ماژول برای جلوگیری از نمایش نقشه نادرست متوقف شد.';",
        "error.dataset.msArchiveState='gis';error.textContent=message('gis');")
    js = single_replace(js,
        "banner.textContent='این ماژول در فایل‌های نصب‌شده پیدا نشد یا با نسخه بررسی‌شده مطابقت ندارد. برای جلوگیری از نمایش نسخه اشتباه باز نشد.';",
        "banner.dataset.msArchiveState='failed';banner.textContent=message('failed');")
    js = single_replace(js, "frame.title=label;frame.dataset.ms24Route=route;",
        "frame.title=liveEnglish()?ARCHIVE_EN[route]:(MODULES[route].title||label);frame.dataset.ms24Route=route;")
    js = single_replace(js,
        " for(const frame of document.querySelectorAll('iframe.ms23-module-frame')){",
        """ for(const status of document.querySelectorAll('[data-ms-archive-state]')){
     const key=status.dataset.msArchiveState;
     if(['loading','failed','gis'].includes(key))status.textContent=message(key);
   }
   for(const frame of document.querySelectorAll('iframe.ms23-module-frame')){
     const route=frame.dataset.ms24Route;
     if(Object.prototype.hasOwnProperty.call(MODULES,route))frame.title=liveEnglish()?ARCHIVE_EN[route]:MODULES[route].title;""")
    js = single_replace(js,
        'const NAV_EN={"isohyet":"Station rainfall / isohyet maps","toolbox-full":"Complete meteorological toolbox","verify-forecast":"Forecast verification","bulletin-maps":"Bulletin weather maps","convert-unit":"Meteorological unit conversion","toolbox-spatial":"Station precipitation IDW"};',
        'const NAV_EN=ARCHIVE_EN;')
    files[TARGET] = js.encode("utf-8")
    expected = set(files)
    if len(files) != 15 or any(item in expected for item in OLD):
        raise RuntimeError("Unexpected dependency count; abort")
    # All known scientific/GIS payloads MUST match the old staging archive.
    for name in ("online/station_isohyet_v26.html","online/meteo_toolbox_v22.html",
                 "online/forecast_verification_v22.html","online/bulletin_maps_v21.html",
                 "online/atlas_stations_v28.json","assets/map_layers.js"):
        with zipfile.ZipFile(source) as z:
            if z.read(name) != files[name]:
                raise RuntimeError("Scientific engine or GIS data changed: "+name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for name in sorted(files):
            z.writestr(name, files[name])
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:
            raise RuntimeError("Output ZIP failed CRC")
    return hashlib.sha256(files["index.html"]).hexdigest()


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("stage28",type=Path)
    ap.add_argument("stage29_out",type=Path)
    args=ap.parse_args()
    print("Staged index SHA256:",rebuild(args.stage28,args.stage29_out))
