#!/usr/bin/env python3
"""Streaming importer: supplied 2026-11-16 OSM *nodes*, no assumptions about weather station identity.
Reads 849,897 x 98 Excel worksheet via OOXML streaming so memory does not scale with row count.
Creates indexed SQLite gazetteer, lightweight mountain JSON, and review CSV.
"""
import os,sys,re,json,csv,sqlite3,time,zipfile,unicodedata,collections
from lxml import etree
from pathlib import Path
SRC=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
SETTLEMENT={'city','town','village','hamlet','isolated_dwelling','farm','locality','neighbourhood','quarter','suburb','borough','municipality','allotments'}
PEAK={'peak','volcano','hill'}
GEO_NAT={'saddle','mountain_range','ridge','plateau','valley','cliff'}
FARM={'farmyard','farmland','orchard','vineyard','greenhouse_horticulture'}
DB=sqlite3.connect(str(OUT/'osm_geonames_v86.sqlite'))
DB.executescript('''PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;
CREATE TABLE places(id INTEGER PRIMARY KEY, name TEXT NOT NULL, name_fa TEXT, name_en TEXT, alt_name TEXT, latitude REAL NOT NULL, longitude REAL NOT NULL, category TEXT, subtype TEXT, elevation_m REAL, province_hint TEXT, county_hint TEXT, wikidata TEXT, osm_url TEXT NOT NULL, evidence TEXT NOT NULL);
CREATE INDEX idx_name ON places(name); CREATE INDEX idx_kind ON places(category,subtype);
CREATE INDEX idx_coords ON places(latitude,longitude);
CREATE VIRTUAL TABLE names USING fts5(name_norm,osm_id UNINDEXED, tokenize='unicode61 remove_diacritics 2');
CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
''')
stat=collections.Counter();kinds=collections.Counter();invalid=[];peaks=[];peek=[];farms=0;seenids=set()
fa_re=re.compile('[\u0600-\u06ff]'); ele_re=re.compile(r'^\s*([-+]?\d+(?:[.,]\d+)?)\s*(?:m|meters?|metres?|متر)?\s*$',re.I)
header={}
def norm(s):
 s=unicodedata.normalize('NFKC',str(s or '')).replace('ي','ی').replace('ك','ک').replace('ۀ','ه').replace('\u200c',' ')
 s=''.join(c for c in s if unicodedata.category(c)!='Mn')
 return re.sub(r'\s+',' ',re.sub(r'[^\w\u0600-\u06ff ]+',' ',s)).strip().casefold()
def num(s):
 try:return float(str(s).replace('٫','.').replace('،','.'))
 except:return None
def elev(s):
 if s is None or s=='':return None
 m=ele_re.match(str(s))
 if not m: return None
 try: v=float(m.group(1).replace(',','.'));return round(v,1) if -500<=v<=9000 else None
 except:return None
def rows():
 with zipfile.ZipFile(SRC) as z:
  with z.open('xl/worksheets/sheet1.xml') as f:
   for event,row in etree.iterparse(f,events=('end',),tag=NS+'row',huge_tree=True):
    d={}
    for c in row:
     if c.tag!=NS+'c':continue
     ref=c.get('r','');col=re.match('[A-Z]+',ref)
     if col is None:continue
     cidx=0
     for ch in col.group():cidx=cidx*26+ord(ch)-64
     val=''
     for x in c:
      if x.tag==NS+'v':val=x.text or '';break
      if x.tag==NS+'is':val=''.join(x.itertext());break
     if val!='':d[cidx]=val
    yield d
    row.clear()
    while row.getprevious() is not None:del row.getparent()[0]

with (OUT/'peaks_without_elevation_v86.csv').open('w',encoding='utf-8-sig',newline='') as missing:
 mw=csv.writer(missing);mw.writerow(['osm_id','name','name_fa','name_en','latitude','longitude','natural','osm_url','reason'])
 batch=[];nbatch=[]
 for j,d in enumerate(rows()):
  if j==0:
   header={ix:str(v) for ix,v in d.items()};print('header',len(header),flush=True);continue
  def f(x):
   try:return d.get(next(k for k,v in header.items() if v==x),'')
   except StopIteration:return ''
  if not header.get(1)=='osm_id':raise Exception('unexpected schema')
  # Fixed column indices (validated by explicit header row)
  osm=num(d.get(1));la=num(d.get(2));lo=num(d.get(3));name=(d.get(12) or d.get(10) or d.get(11) or '').strip()
  if osm is None or la is None or lo is None or not (24<la<41.0 and 43<lo<64.5):stat['bad_coord']+=1;continue
  oid=int(osm);natural=d.get(23,'');place=d.get(18,'');landuse=d.get(34,'');man=d.get(24,'');
  cat=None;kind=''
  if natural in PEAK:cat='mountain';kind=natural
  elif place in SETTLEMENT:cat='settlement';kind=place
  elif natural in GEO_NAT:cat='terrain';kind=natural
  elif landuse in FARM:cat='agricultural';kind=landuse
  elif man in {'weather_station','monitoring_station','observatory'}:cat='weather_reference';kind=man
  elif d.get(6)=='weather_station' or d.get(6)=='meteorological_station':cat='weather_reference';kind=d.get(6)
  if cat is None:stat['other_categories']+=1;continue
  if not name:stat['eligible_unnamed']+=1;continue
  fa=(d.get(12) or (d.get(10) if fa_re.search(d.get(10,'')) else '') or '').strip()
  en=(d.get(11) or (d.get(10) if not fa_re.search(d.get(10,'')) else '') or '').strip()
  el=elev(d.get(4) or d.get(17))
  if d.get(4) and el is None:stat['invalid_ele']+=1
  hint=(d.get(48) or d.get(49) or d.get(66) or d.get(65) or '').strip() # AV AW BN AR; hints not verified
  county=(d.get(50) or d.get(44) or '').strip() # AX district, AR city; label as hint only
  osm_url='https://www.openstreetmap.org/node/'+str(oid)
  alt=(d.get(13) or '').strip()
  evidence='osm_node_geometry_and_tags_not_sensor_verified'
  batch.append((oid,name,fa,en,alt,la,lo,cat,kind,el,hint,county,d.get(52,''),osm_url,evidence))
  names={norm(n) for n in [name,fa,en,*re.split('[;|،]',alt)] if n.strip()}
  nbatch.extend((nm,oid) for nm in names if nm)
  stat['selected']+=1;kinds[cat+':'+kind]+=1
  if cat=='mountain':
   if el is not None and el>=500:
    peaks.append(dict(id='osm'+str(oid),name_fa=fa or name,name_en=en or name,lat=la,lon=lo,elevation_m=el,kind=kind,source=osm_url,alt_name=alt,province_hint=hint))
    stat['peak_elevation']+=1
   else:
    mw.writerow([oid,name,fa,en,la,lo,kind,osm_url,'missing_or_out_of_range_ele'])
    stat['peak_missing_ele']+=1
  if len(batch)>=2500:
   DB.executemany('INSERT INTO places VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',batch)
   DB.executemany('INSERT INTO names(name_norm,osm_id) VALUES (?,?)',nbatch)
   DB.commit();batch=[];nbatch=[]
  if j%150000==0:print('progress',j,dict(stat),flush=True)
 if batch:
  DB.executemany('INSERT INTO places VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',batch)
  DB.executemany('INSERT INTO names(name_norm,osm_id) VALUES (?,?)',nbatch)
  DB.commit()
stat['total_xlsx_rows']=j
# OSM coordinates direct, no authoritative elevation if source ele absent
peaks.sort(key=lambda o:(-o['elevation_m'],o['id']))
with (OUT/'mountain_peaks_osm_v86.json').open('w',encoding='utf-8') as f:json.dump({'source':'OpenStreetMap contributors via user-provided Geofabrik PBF-derived Excel, OSM nodes only, 2026-11-16','elevation_note':'ele tag is community-supplied, NOT DEM-validated; weather forecasts approximate free-air conditions','count':len(peaks),'peaks':peaks},f,ensure_ascii=False,separators=(',',':'))
with (OUT/'osm_geonames_summary_v86.json').open('w',encoding='utf-8') as f:json.dump({'counts':stat,'types':kinds,'input':str(SRC.name),'source_coverage':'OSM nodes only; ways and relations omitted'},f,ensure_ascii=False,indent=2)
DB.executemany('INSERT INTO meta VALUES (?,?)',[('source','User PBF-derived Excel, OSM nodes as of 2026-11-16'),('attribution','© OpenStreetMap contributors (ODbL); Geofabrik extract'),('peak_count',str(len(peaks))),('settlement_count',str(sum(v for k,v in kinds.items() if k.startswith('settlement:'))))]);DB.commit();DB.execute('PRAGMA wal_checkpoint(TRUNCATE)');DB.execute('VACUUM');DB.close()
print('DONE',json.dumps(dict(stat),ensure_ascii=False),flush=True)
