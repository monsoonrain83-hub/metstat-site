"""Stage authoritative US state/county IDs and original-resolution geometry.

No simplification, snapping, translation guessing, host access or automatic release.
Original source archives retained. GeoJSON staging coordinates stay in source CRS.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlsplit
from zipfile import ZipFile

import pyogrio
from shapely import coverage_is_valid, union_all, get_coordinates
from shapely.geometry import mapping
import numpy as np

YEAR=2026
BASE=f"https://www2.census.gov/geo/tiger/TIGER{YEAR}"
ROOT=Path("census-stage")
MAX_BYTES=256*1024*1024

def download(level):
    name=f"tl_{YEAR}_us_{level.lower()}.zip"
    url=f"{BASE}/{level}/{name}"
    path=ROOT/name
    h=hashlib.sha256()
    n=0
    with urlopen(Request(url,headers={"User-Agent":"MetStat geographic validation"}),timeout=120) as r, path.open("xb") as f:
        if urlsplit(r.geturl()).scheme!="https" or urlsplit(r.geturl()).hostname!="www2.census.gov":
            raise ValueError("unexpected source redirect")
        while chunk:=r.read(1024*1024):
            n+=len(chunk)
            if n>MAX_BYTES: raise ValueError("archive exceeds size limit")
            h.update(chunk); f.write(chunk)
    with ZipFile(path) as z:
        if len(z.infolist())>20 or sum(i.file_size for i in z.infolist())>1024*1024*1024:
            raise ValueError("unreasonable archive expansion")
        if any("/" in i.filename or "\\" in i.filename or i.filename in (".","..") for i in z.infolist()):
            raise ValueError("unexpected source archive paths")
        if z.testzip(): raise ValueError("corrupted archive")
    return path,{"url":url,"sha256":h.hexdigest(),"bytes":n}

def read(path, level):
    cols=["STATEFP","GEOID","NAME","NAMELSAD"]+(["COUNTYFP"] if level=="COUNTY" else [])
    df=pyogrio.read_dataframe(path,columns=cols)
    if df.crs is None: raise ValueError("missing source CRS")
    records={}
    for r in df.itertuples(index=False):
        code=str(r.GEOID)
        state=str(r.STATEFP)
        if not re.fullmatch(r"[0-9]{2}",state): raise ValueError("invalid state code")
        if code in records or code!=(state+str(r.COUNTYFP) if level=="COUNTY" else state):
            raise ValueError("invalid/duplicate official ID")
        if len(code)!=(5 if level=="COUNTY" else 2) or not code.isascii() or not code.isdigit():
            raise ValueError("invalid GEOID")
        name=str(r.NAMELSAD)
        if not name.strip() or re.search(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]",name):
            raise ValueError("missing or unexpected source English name")
        g=r.geometry
        if g is None or g.is_empty or not g.is_valid or g.geom_type not in ("Polygon","MultiPolygon") or g.has_z:
            raise ValueError("invalid source geometry "+code)
        xy=get_coordinates(g)
        if not np.isfinite(xy).all(): raise ValueError("nonfinite geometry")
        records[code]={"state":state,"en":name,"g":g}
    return df.crs,records

def save(name, rows):
    path=ROOT/name
    # No rounding or geometry operations when serializing.
    data={"type":"FeatureCollection","features":[
        {"type":"Feature","id":"US:"+k,"properties":{"geoid":k,"parent":"US:"+v["state"] if len(k)==5 else "US","name_en":v["en"],"name_fa":None,"fa_approved":False},"geometry":mapping(v["g"])}
        for k,v in sorted(rows.items())]}
    path.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"),allow_nan=False),encoding="utf-8")
    return {"file":name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}

def run():
    ROOT.mkdir(exist_ok=False)
    report={"year":YEAR,"status":"staging only","iran_touched":False,"source":{},"states":{}}
    for level in ("STATE","COUNTY"):
        path,meta=download(level); report["source"][level]=meta
        if level=="STATE": crs,states=read(path,level)
        else: crs2,counties=read(path,level)
    if crs!=crs2 or not crs.is_geographic: raise ValueError("source CRS mismatch")
    report["crs"]=crs.to_string()
    if any(r["state"] not in states for r in counties.values()): raise ValueError("orphan county")
    report["counts"]={"states":len(states),"counties":len(counties)}
    report["state_file"]=save("states.geojson",states)
    for state,record in sorted(states.items()):
        subset={k:v for k,v in counties.items() if v["state"]==state}
        if not subset:
            report["states"][state]={"count":0,"note":"no county source records"}
            continue
        g=record["g"]
        gs=[v["g"] for v in subset.values()]
        union=union_all(gs)
        report["states"][state]={
            "count":len(subset),"parent_source":"STATEFP",
            "exact_within_parent":sum(g.covers(x) for x in gs),
            "coverage_valid":bool(coverage_is_valid(gs)),
            "union_equals_state":bool(union.equals(g)),
            "outside_area_native_degrees2":union.difference(g).area,
            "uncovered_area_native_degrees2":g.difference(union).area,
            "chunk":save("counties-"+state+".geojson",subset)}
    report["state_coverage_valid"]=bool(coverage_is_valid([v["g"] for v in states.values()]))
    report["release_approved"]=False
    (ROOT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="states"},indent=2))
    print(json.dumps({"states_with_counties":sum(bool(v["count"]) for v in report["states"].values()),
                      "exact_union_states":sum(v.get("union_equals_state",False) for v in report["states"].values()),
                      "all_counties_within_parent":sum(v.get("exact_within_parent",0) for v in report["states"].values()),
                      "invalid_coverage_states":[k for k,v in report["states"].items() if v.get("coverage_valid") is False]},indent=2))

if __name__=="__main__":
    run()
