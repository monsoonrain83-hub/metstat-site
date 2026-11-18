#!/usr/bin/env python3
"""Build additive, attribution-preserving MetStat OSM settlement layer from r86 private shards."""
import zipfile,json,collections,hashlib,pathlib,re
root=pathlib.Path('/mnt/data/metstat_r87_work')
z=zipfile.ZipFile('/mnt/data/MetStat_r86_PRIVATE_GEO_INSTALL.zip')
byid={}
for fn in z.namelist():
 if fn.endswith('.json') and not fn.endswith('_manifest.json'):
  for rows in json.loads(z.read(fn)).values():
   for x in rows:
    if x[0] not in byid:byid[x[0]]=x
kind={'city':0,'town':1,'municipality':1,'borough':2,'suburb':2,'quarter':2,'neighbourhood':3,'village':4,'hamlet':5,'locality':5,'isolated_dwelling':5,'farm':6,'farmyard':6,'farmland':6,'orchard':6}
rows=[]
for r in byid.values():
 if r[6] not in ('settlement','agricultural') or not(r[2] or r[3]):continue
 lat,lon=r[4],r[5]
 if not(isinstance(lat,(float,int)) and isinstance(lon,(float,int)) and 24<lat<41 and 43<lon<65):continue
 t=r[7];i=kind.get(t,5)
 rows.append([round(float(lat),6),round(float(lon),6),(r[2] or r[1] or '').replace('ك','ک').replace('ي','ی'),r[3] or '',i,r[0],r[9] or '',r[10] or ''])
rows.sort(key=lambda r:(r[4],r[6],r[7],r[5]))
obj={'version':'87','source':'OpenStreetMap contributors, Geofabrik Iran PBF 2026-11-16, supplied by user (nodes only)','license':'ODbL','attribution':'© OpenStreetMap contributors · https://www.openstreetmap.org/copyright','fields':['lat','lon','name_fa','name_en','class','osm_node_id','province','county'],'classes':['city','town','suburb','neighbourhood','village','hamlet','agricultural'],'nodes':rows}
out=root/'public/data/osm_settlements_v87.json';out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')))
counts=collections.Counter(x[4] for x in rows)
(root/'dataset_metrics.json').write_text(json.dumps({'total':len(rows),'by_class':{obj['classes'][i]:counts[i] for i in range(7)},'source_ids_unique':len(set(x[5] for x in rows)),'data_bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
print('OUTPUT',out,'bytes',out.stat().st_size,'count',len(rows),'classes',counts)
