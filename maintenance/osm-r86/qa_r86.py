#!/usr/bin/env python3
import subprocess,re,hashlib,json,sqlite3,os,urllib.request,time,zipfile,shutil,pathlib,collections
from pathlib import Path
W=Path(__file__).parent
source=Path('/mnt/data/metstat_r85_audit/index_r85.html')
idx=W/'index_r86.html';rain=W/'station_isohyet_r86.html';php=W/'osm_place_lookup_v86.php'
res={}
for title,p in [('index',idx),('isohyet',rain)]:
 s=p.read_text(encoding='utf-8'); scripts=re.findall(r'<script\b[^>]*>(.*?)</script\s*>',s,re.I|re.S)
 cnt=0;err=[]
 for i,js in enumerate(scripts):
  if not js.strip() or not js.strip().startswith(('<!--','<![CDATA[')) and 'src=' in js[:60]:continue
  t=W/f'_temp_{title}_script_{i}.js';t.write_text(js,encoding='utf-8')
  p0=subprocess.run(['node','--check',str(t)],capture_output=True,text=True)
  if p0.returncode:err.append({'script':i,'stderr':p0.stderr[-450:]})
  else:cnt+=1
  t.unlink()
 res[title]={'inline_js_ok':cnt,'errors':err,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if err:print('JS FAIL',title,err)
 try:
  from bs4 import BeautifulSoup
  soup=BeautifulSoup(s,'html.parser');ids=[e.get('id') for e in soup.select('[id]')];d=[(id,n) for id,n in collections.Counter(ids).items() if n>1];res[title]['duplicate_ids']=d
 except Exception as e:res[title]['html_parse_note']=str(e)
try:
 from tinycss2 import parse_stylesheet
 styles=re.findall(r'<style\b[^>]*>(.*?)</style>',idx.read_text(encoding='utf8'),re.I|re.S)
 errs=[str(t) for css in styles for t in parse_stylesheet(css,skip_comments=True,skip_whitespace=True) if t.type=='error']
 res['index']['css_styles']=len(styles);res['index']['css_parse_errors']=errs[:15]
except Exception as e:res['index']['css_parse_note']=str(e)
a=json.load(open(W/'mountain_peaks_osm_v86.json',encoding='utf8'))
c=sqlite3.connect(W/'osm_geonames_v86.sqlite');res['osm']={'db_places':c.execute('select count(*) from places').fetchone()[0], 'db_names':c.execute('select count(*) from names').fetchone()[0], 'mountain_peaks_with_ele':a['count'],'missing_elevation':sum(1 for _ in open(W/'peaks_without_elevation_v86.csv',encoding='utf-8-sig'))-1};c.close()
subprocess.run(['php','-l',str(php)],check=True)
# PHP API tests against real shard files in a cPanel-shaped local layout
host=W/'test_host';os.makedirs(host/'public_html'/'online',exist_ok=True);os.makedirs(host/'metstat_station_private',exist_ok=True)
shard=host/'metstat_station_private'/'osm_places_shards_v86'
if not shard.exists():shard.symlink_to(W/'osm_places_shards_v86',target_is_directory=True)
shutil.copy2(php,host/'public_html'/'online'/'osm_place_lookup_v86.php')
server=subprocess.Popen(['php','-S','127.0.0.1:18786','-t',str(host/'public_html')],stdout=subprocess.DEVNULL,stderr=(W/'php_test.log').open('w'))
try:
 time.sleep(.4)
 url='http://127.0.0.1:18786/online/osm_place_lookup_v86.php'
 status=json.load(urllib.request.urlopen(url+'?a=status',timeout=10));assert status['ready']
 def query(names):
  data=json.dumps({'queries':[{'name':n} for n in names]},ensure_ascii=False).encode('utf8')
  req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'})
  return json.load(urllib.request.urlopen(req,timeout=20))
 v=query(['چابکسر','امامزاده اسحاق','شوییل','لشگان','دماوند'])
 assert v['ok'] and len(v['results'])==5
 g=[(o['name'],o['total_exact_osm_nodes'],o['places'][0]['lat'] if o['places'] else None) for o in v['results']]
 assert v['results'][0]['total_exact_osm_nodes']>=1 and v['results'][1]['total_exact_osm_nodes']>=1
 assert v['results'][0]['places'][0]['approximate'] and v['results'][0]['places'][0]['unverified']
 def areaquery(province,county):
  body=json.dumps({'queries':[{'name':'امامزاده اسحاق','province':province,'county':county}]},ensure_ascii=False).encode('utf8')
  req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json'})
  return json.load(urllib.request.urlopen(req,timeout=20))['results'][0]['within_reported_admin']
 assert areaquery('گیلان','شفت')==1
 assert areaquery('گیلان','رودسر')==0
 assert areaquery('فارس','شفت')==0
 res['php_admin_tests']={'gilan_shaft':1,'wrong_county':0,'wrong_province':0}
 res['php']={'status':'ready','sample_results':g,'notice':v['notice']}
finally:
 server.terminate();server.wait(timeout=10)
json.dump(res,open(W/'QA_results_v86.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
print(json.dumps(res,ensure_ascii=False,indent=2)[:4500]);assert all(not res[x]['errors'] for x in ('index','isohyet'))
