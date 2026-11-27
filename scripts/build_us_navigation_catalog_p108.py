"""P1-08: create a lightweight, locale-safe navigation catalog from verified P1-07 US sources.

Staging only. Geometry is not rewritten; native EPSG:4269 is explicitly recorded.
No Persian-name guesses, no automatic release, no Iran inputs.
"""
import hashlib
import json
import re
from pathlib import Path

SRC=Path("census-stage")
OUT=Path("census-catalog")
PINS={"STATE":"2e17ea40dff3e00163eec87a26efa0b0ff7e8fe364a191bf1a7754dcb49ea326",
      "COUNTY":"b527c9ba7aeb8f17ef118f026eae5e5a938aa1d00b873bc32342d0dce59321c0"}
STATE_PIN="819d650b335e3defaca327adeca31e42ec0216dabfa6f6754abcb6513978bd73"
AR=re.compile(r"[\u0600-\u06ff\u0750-\u077f\u0870-\u089f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]")
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        while b:=f.read(1024*1024): h.update(b)
    return h.hexdigest()

def verify(p, expected):
    if not p.is_file() or p.is_symlink() or digest(p)!=expected:
        raise ValueError("source mismatch: "+p.name)

def extract(p, parent, n):
    data=json.loads(p.read_text(encoding="utf-8"))
    if data.get("type")!="FeatureCollection": raise ValueError("invalid source collection")
    rows=[]
    ids=set()
    for f in data["features"]:
        props=f["properties"]
        code=props["geoid"]
        name=props["name_en"]
        if not re.fullmatch(r"[0-9]{"+str(n)+"}",code) or code in ids or f["id"]!="US:"+code:
            raise ValueError("invalid identity")
        if props["parent"]!=parent or (n==5 and code[:2]!=parent[3:]):
            raise ValueError("invalid official parent")
        if not isinstance(name,str) or not name.strip() or AR.search(name) or any(ord(c)<32 for c in name):
            raise ValueError("invalid English name")
        if props.get("name_fa") is not None or props.get("fa_approved") is not False:
            raise ValueError("unreviewed translation state changed")
        ids.add(code)
        rows.append({"id":f["id"],"parent":parent,"name_en":name,"name_fa":None,
                     "fa_approved":False})
    return sorted(rows,key=lambda r:r["id"])

def write(name,data):
    p=OUT/name
    p.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"),allow_nan=False),encoding="utf-8")
    return {"file":name,"bytes":p.stat().st_size,"sha256":digest(p)}

def main():
    OUT.mkdir(exist_ok=False)
    report=json.loads((SRC/"report.json").read_text())
    if report["year"]!=2026 or report["crs"]!="EPSG:4269" or report["iran_touched"] is not False:
        raise ValueError("unexpected source report")
    if report["counts"]!={"states":56,"counties":3235} or report["state_coverage_valid"] is not True:
        raise ValueError("source coverage changed")
    for level,pin in PINS.items():
        verify(SRC/("tl_2026_us_"+level.lower()+".zip"),pin)
    verify(SRC/"states.geojson",STATE_PIN)
    states=extract(SRC/"states.geojson","US",2)
    if len(states)!=56 or {r["id"][3:] for r in states}!=set(report["states"]):
        raise ValueError("state list mismatch")
    chunks={}
    total=0
    for state in states:
        code=state["id"][3:]
        r=report["states"][code]
        if r["coverage_valid"] is not True or r["union_equals_state"] is not True or r["exact_within_parent"]!=r["count"]:
            raise ValueError("source state coverage failed: "+code)
        name="counties-"+code+".geojson"
        if r["chunk"]["file"]!=name: raise ValueError("unexpected chunk path")
        verify(SRC/name,r["chunk"]["sha256"])
        rows=extract(SRC/name,state["id"],5)
        if len(rows)!=r["count"]: raise ValueError("county count mismatch")
        total+=len(rows)
        chunks[code]={"catalog":write("counties-"+code+".json",rows),
                      "geometry":{"file":name,"sha256":r["chunk"]["sha256"],"bytes":r["chunk"]["bytes"],"native_crs":"EPSG:4269"},
                      "count":len(rows)}
    if total!=3235: raise ValueError("missing county")
    result={"schema":1,"country":"US","year":2026,"status":"review-only",
            "release_approved":False,"states":states,"chunks":chunks,
            "state_geometry":{"file":"states.geojson","sha256":STATE_PIN,"native_crs":"EPSG:4269"},
            "language":{"en":"source name","fa":"pending review; never fallback to English in Persian release"},
            "counts":{"states":len(states),"counties":total}}
    index=write("index.json",result)
    print(json.dumps({"index":index,"states":len(states),"counties":total,
                      "catalog_files":len(chunks)+1,
                      "total_catalog_bytes":sum(p.stat().st_size for p in OUT.glob("*.json")),
                      "max_county_catalog_bytes":max(v["catalog"]["bytes"] for v in chunks.values()),
                      "geometry_changed":False,"release_approved":False},indent=2))

if __name__=="__main__":
    main()
