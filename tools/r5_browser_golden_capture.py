#!/usr/bin/env python3
"""Measure only the exact administrator R5 file in isolated local Chromium.

Reference has no real NWP; this tool never performs cPanel upload or network I/O.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from tools.r5_uiux_report_gate import CONTRACT, validate

JS = """() => {
const get = s => document.querySelector(s);
const rect = s => {const e=get(s); if(!e)return {};const r=e.getBoundingClientRect();
return {x:+r.x.toFixed(2),width:+r.width.toFixed(2),height:+r.height.toFixed(2)}};
const css=getComputedStyle(document.documentElement);
return {
 nav:document.querySelectorAll('#mainNav .nav-button').length,
 models:document.querySelectorAll('#mapModelRail .model-status').length,
 geographies:[...document.querySelectorAll('.geo-bar select')].map(e=>e.id),
 lang:document.documentElement.lang,dir:document.documentElement.dir,
 tokens:Object.fromEntries(['--sky','--paper','--scarlet'].map(k=>[k,css.getPropertyValue(k).trim().toLowerCase()])),
 sidebar:rect('.sidebar'),map:rect('.map-card'),header:rect('.header'),
 appMinWidth:getComputedStyle(get('.app')).minWidth
}}"""


def capture(reference: Path, out: Path, chromium: str = "/usr/bin/chromium") -> dict:
    contract=json.loads(CONTRACT.read_text(encoding="utf8"))
    data=reference.read_bytes()
    got=sha256(data).hexdigest()
    if got != contract["source_sha256"]:
        raise ValueError("Reference SHA changed. No substitution of R7, R9 or a different R5")
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True,exist_ok=True)
    report={"sha256":got,"source":contract["source"],"viewports":[]}
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path=chromium,args=["--no-sandbox"])
        try:
            for golden in contract["viewports"]:
                w,h=golden["width"],golden["height"]
                page=browser.new_page(viewport={"width":w,"height":h},device_scale_factor=1)
                errors=[]
                page.on("pageerror",lambda exc:errors.append(str(exc)))
                # Sandboxed reference includes CSP connect-src 'none'; no external fetch.
                page.set_content(data.decode("utf8"),wait_until="domcontentloaded")
                page.wait_for_timeout(100)
                metrics=page.evaluate(JS)
                name=f"R5_{w}x{h}.png"
                page.screenshot(path=str(out/name),full_page=False)
                report["viewports"].append({"viewport":[w,h],"measurements":metrics,
                                           "passed":len(errors)==0,"page_errors":errors,
                                           "screenshot":name})
                page.close()
        finally:
            browser.close()
    report["reference_not_live_data"]=True
    result=validate(report,contract)
    report["gate"]=result
    (out/"R5_GOLDEN_BROWSER_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("reference",type=Path)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--chromium",default="/usr/bin/chromium")
    args=p.parse_args()
    try:result=capture(args.reference,args.out,args.chromium)
    except Exception as exc:
        print(json.dumps({"passed":False,"error":str(exc)},ensure_ascii=False))
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
