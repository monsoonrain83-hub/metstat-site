#!/usr/bin/env python3
import json,subprocess,sys,math,csv,unicodedata,re
from pathlib import Path
w=Path(__file__).parent
src=Path('/mnt/data/metstat_r85_audit/index_r85.html');peaks=json.loads((w/'mountain_peaks_osm_v86.json').read_text())['peaks']
node=r'''
const fs=require('fs'), vm=require('vm');const src=fs.readFileSync(process.argv[1],'utf8');const keys=['MT_PEAKS','MT_EXTRA','MT_NEW','MT_WORLD'];const out={};
for(const key of keys){const pat=new RegExp('const\\s+'+key+'\\s*=\\s*(\\[[\\s\\S]*?\\]);');const m=src.match(pat);if(!m)throw Error('Missing '+key);out[key]=vm.runInNewContext(m[1],{}, {timeout:3000});}
console.log(JSON.stringify(out));
'''
raw=subprocess.run(['node','-e',node,str(src)],capture_output=True,text=True,check=True);d=json.loads(raw.stdout)
all_peak=[a for arr in d.values() for a in arr];ir=[p for p in all_peak if len(p)>6 and p[6]=='ir']
fa=lambda t:re.sub(r'\s+',' ',str(t or '').replace('ي','ی').replace('ك','ک').replace('\u200c',' ')).strip().lower()
def dist(a,b):
 dy=(a[3]-b['lat'])*111.2;dx=(a[4]-b['lon'])*111.2*math.cos((a[3]+b['lat'])/2*math.pi/180);return math.hypot(dx,dy)
issues=[];close_count=0
for a in ir:
 same=[p for p in peaks if fa(p['name_fa'])==fa(a[1]) or fa(p['name_en'])==fa(a[2])]
 if not same:continue
 near=min(same,key=lambda p:dist(a,p));km=dist(a,near)
 if km<.7 and abs(a[5]-near['elevation_m'])<150:close_count+=1
 if km>1.0 or abs(a[5]-near['elevation_m'])>200:
  issues.append([a[0],a[1],a[3],a[4],a[5],near['id'],near['name_fa'],near['lat'],near['lon'],near['elevation_m'],round(km,2),round(near['elevation_m']-a[5]),near['source'],'review_coordinates_or_summit_identity'])
issues.sort(key=lambda x:-x[10]);
with open(w/'mountain_existing_vs_osm_review_v86.csv','w',encoding='utf-8-sig',newline='') as f:
 o=csv.writer(f);o.writerow(['curated_id','curated_fa','curated_lat','curated_lon','curated_ele_m','osm_id','osm_fa','osm_lat','osm_lon','osm_ele_m','distance_km','elevation_diff_m','osm_source','status']);o.writerows(issues)
report={'curated_peak_total':len(all_peak),'curated_iran_peak_total':len(ir),'osm_peak_total':len(peaks),'curated_near_same_within_0_7km_and_150m':close_count,'curated_osm_conflicts_needing_review':len(issues),'top_conflicts':issues[:10]}
(w/'mountain_conflict_summary_v86.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2)[:2300])
