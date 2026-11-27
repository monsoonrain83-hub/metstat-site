"""P1-05: pinned foreign boundary staging, never a host publisher."""
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen
from shapely import coverage_is_valid, union_all
from shapely.geometry import shape
from shapely.strtree import STRtree

PIN = "8ce2700661a28ee944350e2b329bbabb58d2ff83"
REPO = "wmgeolab/geoBoundaries"
COUNTRIES = ("IRQ", "JPN", "USA")
LIMIT = 80 * 1024 * 1024
AR = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u0870-\u089f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]")
def digest(b):
    return hashlib.sha256(b).hexdigest()

def read(url, limit):
    with urlopen(url, timeout=90) as r:
        b = r.read(limit + 1)
    if len(b) > limit:
        raise ValueError("source exceeds byte limit")
    return b

def get(iso, level, suffix):
    if iso not in COUNTRIES or iso == "IRN" or level not in ("ADM0","ADM1","ADM2"):
        raise ValueError("unapproved staging scope")
    path = f"releaseData/gbOpen/{iso}/{level}/geoBoundaries-{iso}-{level}{suffix}"
    p = read(f"https://raw.githubusercontent.com/{REPO}/{PIN}/{path}", LIMIT)
    if p.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        m = re.fullmatch(rb"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?", p)
        if not m or int(m[2]) > LIMIT:
            raise ValueError("invalid or oversized LFS pointer")
        b = read(f"https://media.githubusercontent.com/media/{REPO}/{PIN}/{path}", int(m[2]))
        if len(b) != int(m[2]) or digest(b) != m[1].decode():
            raise ValueError("LFS integrity mismatch")
        return b
    return p

def inspect(raw, iso, level):
    data = json.loads(raw)
    if data.get("type") != "FeatureCollection":
        raise ValueError("not a FeatureCollection")
    features = data["features"]
    if not 0 < len(features) <= 100000:
        raise ValueError("invalid feature count")
    ids, geoms, names = set(), [], []
    for f in features:
        p = f["properties"]
        sid = p.get("shapeID")
        if not isinstance(sid,str) or not sid or sid in ids:
            raise ValueError("duplicate/missing source ID")
        if p.get("shapeGroup") != iso or p.get("shapeType") != level:
            raise ValueError("source country/level mismatch")
        ids.add(sid)
        g = shape(f["geometry"])
        if g.geom_type not in ("Polygon","MultiPolygon") or g.is_empty or not g.is_valid or g.has_z:
            raise ValueError(f"invalid source polygon: {sid}")
        w,s,e,n = g.bounds
        if not (-180 <= w <= e <= 180 and -90 <= s <= n <= 90):
            raise ValueError("outside WGS84")
        for poly in ([g] if g.geom_type=="Polygon" else g.geoms):
            for ring in [poly.exterior,*poly.interiors]:
                coords=list(ring.coords)
                if any(abs(a[0]-b[0])>180 for a,b in zip(coords,coords[1:])):
                    raise ValueError("unreviewed antimeridian edge")
        geoms.append(g)
        # Source label is evidence, not a verified English or Persian name.
        names.append({"source_id":sid,"source_name":p.get("shapeName"),
                      "source_iso":p.get("shapeISO"),"en":None,"fa":None,
                      "approved":False})
    report = {"features":len(features),"sha256":digest(raw),
              "coverage_valid":bool(coverage_is_valid(geoms)),
              "geometry_changed":False,"names_review_required":len(names)}
    return geoms, names, report

def compare(child, parent):
    tree = STRtree(parent)
    counts = []
    for g in child:
        counts.append(len(tree.query(g, predicate="covered_by")))
    return {"exact_unique_parent":sum(n==1 for n in counts),
            "ambiguous_or_missing_parent":sum(n!=1 for n in counts),
            "union_equals_parent":bool(union_all(child).equals(union_all(parent)))}

def run():
    root = Path("geo-stage")
    root.mkdir(exist_ok=False)
    summary = {"source_commit":PIN,"status":"STAGING ONLY; never publish",
               "iran_touched":False,"countries":{}}
    for iso in COUNTRIES:
        country = root / iso
        country.mkdir()
        layers, report = {}, {}
        summary["countries"][iso] = report
        for level in ("ADM0","ADM1","ADM2"):
            try:
                raw = get(iso, level, ".geojson")
                meta = get(iso, level, "-metaData.json")
                metadata = json.loads(meta)
                if not isinstance(metadata,dict) or not metadata.get("boundaryLicense"):
                    raise ValueError("missing license metadata")
                (country/f"{level}.geojson").write_bytes(raw)
                (country/f"{level}.metadata.json").write_bytes(meta)
                geoms, names, result = inspect(raw,iso,level)
                result["metadata_sha256"] = digest(meta)
                result["license"] = metadata.get("boundaryLicense")
                result["release_approved"] = False
                report[level] = result
                layers[level] = geoms
                (country/f"{level}.names-review.json").write_text(json.dumps(names,ensure_ascii=False),encoding="utf-8")
            except Exception as e:
                report[level] = {"error":str(e)[:500],"release_approved":False}
        for child,parent in (("ADM1","ADM0"),("ADM2","ADM1")):
            if child in layers and parent in layers:
                try:
                    report[f"{child}_vs_{parent}"] = compare(layers[child],layers[parent])
                except Exception as e:
                    report[f"{child}_vs_{parent}"] = {"error":str(e)[:500]}
    (root/"report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if not all("features" in r.get(level,{}) for r in summary["countries"].values() for level in ("ADM0","ADM1","ADM2")):
        raise SystemExit("one or more source layers failed; staging report retained")

if __name__ == "__main__":
    run()
