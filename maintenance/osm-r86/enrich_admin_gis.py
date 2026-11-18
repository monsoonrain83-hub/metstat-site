#!/usr/bin/env python3
"""Overlay OSM point-only gazetteer with existing MetStat 31 province + 489 county boundaries.
Keeps original OSM admin hints, stores separately derived geo_admin fields and provenance.
"""
import sqlite3,sys,json,collections
from pathlib import Path
from shapely.geometry import Point,Polygon,MultiPolygon
from shapely.strtree import STRtree
from shapely.validation import make_valid
from shapely.ops import unary_union
w=Path(__file__).parent
admin=json.load(open(w/'site_admin_polygons_v86.json',encoding='utf8'))
def setup(items):
 shapes=[];names=[]
 for item in items:
  p=item['p'];s=[]
  for poly in item['g']:
   try:
    a=Polygon(poly[0],holes=poly[1:] if len(poly)>1 else None)
    if not a.is_valid:a=make_valid(a)
    if not a.is_empty:s.append(a)
   except Exception:pass
  if not s:continue
  G=unary_union(s) if len(s)>1 else s[0]
  shapes.append(G);names.append(p)
 return shapes,names,STRtree(shapes)
provShapes,provNames,provTree=setup(admin['provinces'])
countyShapes,countyNames,countyTree=setup(admin['counties'])
print('geo',len(provShapes),len(countyShapes),flush=True)
db=sqlite3.connect(str(w/'osm_geonames_v86.sqlite'))
for col in ['province_gis','county_gis']:
 if col not in [x[1] for x in db.execute('pragma table_info(places)')]:db.execute(f'alter table places add column {col} TEXT')
stat=collections.Counter(); updates=[]
for ix,(oid,lat,lon) in enumerate(db.execute('select id,latitude,longitude from places')):
 pt=Point(lon,lat)
 ap=[int(i) for i in provTree.query(pt) if provShapes[int(i)].covers(pt)]
 pn=provNames[ap[0]]['name'] if len(ap)==1 else None
 cs=[int(i) for i in countyTree.query(pt) if countyShapes[int(i)].covers(pt)]
 if pn:cs=[i for i in cs if not countyNames[i].get('ostan') or countyNames[i]['ostan']==pn]
 cn=countyNames[cs[0]]['name'] if len(cs)==1 else None
 if pn:stat['province_matched']+=1
 elif len(ap)>1:stat['province_ambiguous']+=1
 else:stat['province_missing']+=1
 if cn:stat['county_matched']+=1
 elif len(cs)>1:stat['county_ambiguous']+=1
 else:stat['county_missing']+=1
 updates.append((pn,cn,oid))
 if len(updates)>=5000:
  db.executemany('update places set province_gis=?,county_gis=? where id=?',updates)
  db.commit();updates=[]
 if ix and ix%25000==0:print('done',ix,dict(stat),flush=True)
if updates:db.executemany('update places set province_gis=?,county_gis=? where id=?',updates)
db.execute('create index if not exists idx_osm_prov_gis on places(province_gis,county_gis)')
db.execute("insert or replace into meta values ('admin_gis_source','MetStat map_layers.js snapshot 2026-11-14; polygons, not OSM administrative ways')")
db.commit();db.close()
(w/'osm_admin_geofence_v86.json').write_text(json.dumps({'counts':stat,'source_province_polygon_count':len(provNames),'source_county_polygon_count':len(countyNames)},ensure_ascii=False,indent=2))
print('DONE',json.dumps(dict(stat),ensure_ascii=False),flush=True)
