#!/usr/bin/env python3
import csv,sqlite3,unicodedata,re,json,collections
from pathlib import Path
W=Path(__file__).parent;db=sqlite3.connect(str(W/'osm_geonames_v86.sqlite'))
source=Path('/mnt/data/MetStat_v59_Gilan_46_Clean_Input.csv')
def norm(s):
 s=unicodedata.normalize('NFKC',str(s or '')).replace('ي','ی').replace('ك','ک').replace('ۀ','ه').replace('\u200c',' ')
 s=''.join(c for c in s if unicodedata.category(c)!='Mn')
 return re.sub(r'\s+',' ',re.sub(r'[^\w\u0600-\u06ff ]+',' ',s)).strip().casefold()
with source.open(encoding='utf-8-sig',newline='') as f:r=list(csv.DictReader(f))
rows=[];stat=collections.Counter()
for i,e in enumerate(r):
 name=e['نام ایستگاه'];k=norm(name)
 hits=db.execute('''SELECT distinct p.id,p.name,p.name_fa,p.category,p.subtype,p.latitude,p.longitude,p.county_gis,p.osm_url FROM names n join places p on p.id=n.osm_id WHERE n.name_norm=? AND p.province_gis='گیلان' ORDER BY case when p.category='settlement' then 0 else 1 end,p.name''',(k,)).fetchall()
 settlements=[h for h in hits if h[3] in ('settlement','agricultural')]
 status='unique_eligible_locality' if len(settlements)==1 else 'ambiguous_or_multiple' if len(settlements)>1 else 'no_eligible_osm_locality'
 stat[status]+=1
 h=settlements[0] if settlements else (hits[0] if hits else None)
 rows.append([i+1,name,e['بارش'],e['استان'],len(hits),len(settlements),status,h[0] if h else '',h[1] if h else '',h[3] if h else '',h[4] if h else '',h[5] if h else '',h[6] if h else '',h[7] if h else '',h[8] if h else '','نام جغرافیایی OSM است؛ هویت و مختصات ابزار هواشناسی تأیید نیست'])
with (W/'Gilan_46_OSM_locality_coverage_v86.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['row','input_name','precip_mm','reported_province','gis_osm_exact_nodes','settlement_or_agri_nodes','result','suggested_osm_id','suggested_osm_name','osm_category','osm_kind','latitude','longitude','gis_county','osm_url','warning']);wr.writerows(rows)
(W/'Gilan_46_OSM_summary_v86.json').write_text(json.dumps({'total':len(rows),'status':dict(stat)},ensure_ascii=False,indent=2))
print(json.dumps({'total':len(rows),'status':dict(stat),'examples':rows[:6]},ensure_ascii=False,indent=2)[:2900])
