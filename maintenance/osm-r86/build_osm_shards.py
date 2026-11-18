#!/usr/bin/env python3
"""Build portable PHP-readable offline OSM gazetteer shards from SQLite (no PHP SQLite extension required)."""
import sqlite3,sys,hashlib,json,collections,os
from pathlib import Path
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
conn=sqlite3.connect(src);shards=collections.defaultdict(dict);count=0
q='''SELECT n.name_norm,p.id,p.name,p.name_fa,p.name_en,p.alt_name,p.latitude,p.longitude,p.category,p.subtype,p.elevation_m,p.province_gis,p.county_gis,p.province_hint,p.county_hint,p.osm_url FROM names n JOIN places p ON p.id=n.osm_id ORDER BY n.name_norm,p.id'''
for k,id,name,fa,en,alt,lat,lon,cat,kind,elev,prov,county,raw_prov,raw_county,source in conn.execute(q):
 if not k:continue
 path=hashlib.sha1(k.encode('utf-8')).hexdigest()[:2]
 entry=shards[path].setdefault(k,[])
 entry.append([id,name,fa,en,round(lat,7),round(lon,7),cat,kind,elev,prov,county,source,raw_prov,raw_county])
 count+=1
for stem,values in shards.items():
 with (out/(stem+'.json')).open('w',encoding='utf-8') as f: json.dump(values,f,ensure_ascii=False,separators=(',',':'))
with (out/'_manifest.json').open('w',encoding='utf-8') as f:json.dump({'version':'86','source':'OSM Iran node-only Geofabrik 2026-11-16; supplied by user','license':'© OpenStreetMap contributors, ODbL, Geofabrik','aliases':count,'shards':len(shards),'records':conn.execute('SELECT COUNT(*) FROM places').fetchone()[0]},f,ensure_ascii=False,indent=2)
print('shards',len(shards),'aliases',count,'records',conn.execute('SELECT COUNT(*) FROM places').fetchone()[0]);conn.close()
