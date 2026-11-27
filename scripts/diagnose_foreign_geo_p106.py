"""Diagnostic only: assess cross-level mismatch without editing source geometry."""
import hashlib
import json
from pathlib import Path
from pyproj import Geod
from shapely import orient_polygons, union_all
from shapely.geometry import shape, box
from shapely.strtree import STRtree

ROOT = Path("geo-stage")
GEOD = Geod(ellps="WGS84")
PINS = {
    "IRQ": ["fd6bea9e566a234d85ff59efd9cb17e411df7ea5dd469923a1461d6cd975fd0c","2c2adabbc814727b8bdd669feed6efab3b9a27bdc76cea35e036532084eb41d8","757287a87829806eaf2247a76aee870804a6304006ac4b52cb39729be00c5cae"],
    "JPN": ["8da994e4c3301fa3f2e51dcbc23025d61225e6c15ed9c85e4a063ebc1cd11af8","fc30ddd3956821bf4b24828bc53f36683c812eb8c0d9207c46c6c261a2aaa50b","27a0a8fa84fdab6d56b2da1c295b3c71090190d155f6b463bfd5c47beffba972"],
    "USA": ["93ac6f9ed74f3935066fef29d70f8f0f3a139e59089b4cf2b83c2f7326582526","d4f7426c7ba3c49b958b7219fc1503409bab2948efe5917998101d921d77bcf1","81fdd384df8012e5007ed2994a8ab306352f3c48e32cd8ea99182195e8647f43"],
}

def area(g):
    if g.is_empty:
        return 0.0
    if g.geom_type == "Polygon":
        return abs(GEOD.geometry_area_perimeter(orient_polygons(g))[0])
    if hasattr(g, "geoms"):
        return sum(area(p) for p in g.geoms)
    return 0.0

def identity(f):
    p = f["properties"]
    return {"id":p["shapeID"],"name":p.get("shapeName"),"code":p.get("shapeISO")}

def measure(g, parents, tree, parent_ids):
    total = area(g)
    if total <= 0:
        raise ValueError("nonpositive area")
    overlaps = []
    exact = []
    for idx in tree.query(g, predicate="intersects"):
        p = parents[int(idx)]
        if p.covers(g):
            exact.append(parent_ids[int(idx)]["id"])
        a = area(g.intersection(p))
        if a > 0:
            overlaps.append({"parent":parent_ids[int(idx)],"share":a/total})
    overlaps.sort(key=lambda x:(-x["share"],x["parent"]["id"]))
    best = overlaps[0]["share"] if overlaps else 0.0
    second = overlaps[1]["share"] if len(overlaps)>1 else 0.0
    if len(exact)==1:
        classification="exact_geometry"
    elif best >= 0.995 and second <= 0.005:
        classification="near_match_review"
    elif best >= 0.95 and second <= 0.05:
        classification="moderate_mismatch_review"
    else:
        classification="substantial_or_ambiguous"
    return {"class":classification,"best_share":round(best,8),
            "second_share":round(second,8),"exact_parent_ids":exact,
            "overlaps":[{"parent":x["parent"],"share":round(x["share"],8)} for x in overlaps],
            "approved_parent_id":None}

def load(iso, level):
    p = ROOT / iso / (level+".geojson")
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINS[iso][int(level[-1])]:
        raise ValueError("source drift: "+str(p))
    features=json.loads(raw)["features"]
    return [shape(f["geometry"]) for f in features], [identity(f) for f in features]

def compare(iso, lower, upper):
    children, ids=load(iso, lower)
    parents, pids=load(iso, upper)
    tree=STRtree(parents)
    records=[]
    counts={}
    for g, ident in zip(children,ids):
        row=measure(g,parents,tree,pids)
        row["child"]=ident
        records.append(row)
        k=row["class"]
        counts[k]=counts.get(k,0)+1
    child_union=union_all(children)
    parent_union=union_all(parents)
    stats={"child_count":len(children),"parent_count":len(parents),"classes":counts,
           "parent_area_km2":round(area(parent_union)/1e6,3),
           "parent_not_covered_by_children_km2":round(area(parent_union.difference(child_union))/1e6,3),
           "children_outside_parent_km2":round(area(child_union.difference(parent_union))/1e6,3),
           "approved_parent_count":0}
    (ROOT/iso/f"{lower}-to-{upper}-diagnostics.json").write_text(json.dumps(records,ensure_ascii=False),encoding="utf-8")
    return stats

def test():
    parents=[box(0,0,1,1),box(1,0,2,1)]
    ids=[{"id":"A"},{"id":"B"}]
    tree=STRtree(parents)
    assert measure(box(.1,.1,.9,.9),parents,tree,ids)["class"]=="exact_geometry"
    assert measure(box(.1,.1,1.001,.9),parents,tree,ids)["class"]=="near_match_review"
    assert measure(box(.1,.1,1.03,.9),parents,tree,ids)["class"]=="moderate_mismatch_review"
    assert measure(box(.5,.1,1.5,.9),parents,tree,ids)["class"]=="substantial_or_ambiguous"
    assert measure(box(3,0,4,1),parents,tree,ids)["best_share"]==0
    assert measure(box(.1,.1,.9,.9),parents,tree,ids)["approved_parent_id"] is None
    assert area(box(0,0,1,1).intersection(box(1,0,2,1)))==0
    print("7 diagnostic tests passed")

if __name__=="__main__":
    test()
    result={"status":"diagnostic only; no approvals, no geometry edits",
            "countries":{}}
    for iso in PINS:
        assert iso!="IRN"
        meta={}
        for level in ("ADM0","ADM1","ADM2"):
            m=json.loads((ROOT/iso/(level+".metadata.json")).read_text())
            meta[level]={k:m.get(k) for k in ("boundaryYearRepresented","boundarySource-1","boundarySource-2","boundaryLicense","licenseDetail","licenseSource","boundaryID")}
        result["countries"][iso]={"metadata":meta,
             "ADM1_ADM0":compare(iso,"ADM1","ADM0"),
             "ADM2_ADM1":compare(iso,"ADM2","ADM1")}
    (ROOT/"cross-level-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
