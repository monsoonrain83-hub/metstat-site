#!/usr/bin/env python3
"""Surgical index/mountain and isohyet patches; preserve existing private registry and base page logic."""
from pathlib import Path
import sys,hashlib
ROOT=Path(__file__).parent
base=Path(sys.argv[1]); out=Path(sys.argv[2]); rain_in=Path(sys.argv[3]); rain_out=Path(sys.argv[4])
def once(s,old,new,tag):
 c=s.count(old)
 if c!=1:raise AssertionError(f'{tag}: anchor occurrences={c}')
 return s.replace(old,new,1)
idx=base.read_text(encoding='utf-8')
old='const mtAll=()=>MT_PEAKS.concat(typeof MT_EXTRA!=="undefined"?MT_EXTRA:[],typeof MT_NEW!=="undefined"?MT_NEW:[],typeof MT_WORLD!=="undefined"?MT_WORLD:[],MT.my);'
new='''/* r86: OSM named peaks are supplemental, NEVER replace the curated summit catalogue.
 * `ele` is an OSM tag rather than a DEM/field verification; keep source provenance.
 * File is fetched only if user opens mountain weather. */
let MT_OSM_PEAKS=[];
let MT_OSM_STATUS="idle";
let MT_OSM_PROMISE=null;
function mtOsmEsc(s){return String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\\"":"&quot;","'":"&#39;"}[c]||""));}
function mtOsmDistanceKm(a,b){const rad=Math.PI/180,dy=(a[3]-b[3])*111.2,dx=(a[4]-b[4])*111.2*Math.cos((a[3]+b[3])*.5*rad);return Math.hypot(dx,dy);}
async function mtLoadOsmPeaks(){
 if(MT_OSM_PROMISE)return MT_OSM_PROMISE;
 MT_OSM_STATUS="loading";
 MT_OSM_PROMISE=(async()=>{
  const response=await fetch("data/mountain_peaks_osm_v86.json?v=86",{cache:"force-cache"});
  if(!response.ok)throw Error("OSM peaks HTTP "+response.status);
  const data=await response.json();
  if(!Array.isArray(data.peaks)||!data.peaks.length||data.peaks.length>20000)throw Error("Invalid OSM peak data");
  const curated=MT_PEAKS.concat(typeof MT_EXTRA!=="undefined"?MT_EXTRA:[],typeof MT_NEW!=="undefined"?MT_NEW:[],typeof MT_WORLD!=="undefined"?MT_WORLD:[],MT.my);
  const added=[];
  const simplify=s=>String(s||"").replace(/[\u200c\u200d]/g," ").replace(/[ك]/g,"ک").replace(/[ي]/g,"ی").replace(/\s+/g," ").trim().toLowerCase();
  for(const p of data.peaks){
   const lat=+p.lat,lon=+p.lon,el=+p.elevation_m;
   if(!Number.isFinite(lat)||!Number.isFinite(lon)||!Number.isFinite(el)||lat<24||lat>41||lon<43||lon>64.5||el<500||el>9000)continue;
   const name=mtOsmEsc(p.name_fa||p.name_en||""),en=mtOsmEsc(p.name_en||p.name_fa||"");
   if(!name||!p.id||!String(p.id).startsWith("osm"))continue;
   const val=[String(p.id),name,en,lat,lon,el,"ir",""];
   val._osmSource=String(p.source||"");val._osmElevationUnverified=true;
   const near=(a)=>Math.abs(a[5]-el)<150&&mtOsmDistanceKm(a,val)<.7&&(simplify(a[1])===simplify(val[1])||simplify(a[2])===simplify(val[2]));
   if(curated.some(near)||added.some(near))continue;
   added.push(val);
  }
  MT_OSM_PEAKS=added;
  MT_OSM_STATUS="ready";
  return MT_OSM_PEAKS.length;
 })().catch(e=>{MT_OSM_STATUS="unavailable";MT_OSM_PROMISE=null;throw e;});
 return MT_OSM_PROMISE;
}
const mtAll=()=>MT_PEAKS.concat(typeof MT_EXTRA!=="undefined"?MT_EXTRA:[],typeof MT_NEW!=="undefined"?MT_NEW:[],typeof MT_WORLD!=="undefined"?MT_WORLD:[],MT_OSM_PEAKS,MT.my);'''
idx=once(idx,old,new,'mountain catalog')
# Avoid altering user-selected models/current scroll while dynamic catalogue arrives.
idx=once(idx,'window.scrollTo(0,0); mtRender(); try{ vOnPage(); }catch(e){} await mtLoad();',
'''window.scrollTo(0,0); mtRender(); try{ vOnPage(); }catch(e){}
  mtLoadOsmPeaks().then(n=>{if(n&&$("mtMain"))mtRender();}).catch(e=>console.warn("OSM mountain catalog unavailable",e.message));
  await mtLoad();''','mountain on demand')
idx=once(idx,'m.innerHTML=(typeof apWarnBanner==="function"?apWarnBanner():"")+mtHTML(); mtWire();',
'''m.innerHTML=(typeof apWarnBanner==="function"?apWarnBanner():"")+mtHTML()+
 (MT_OSM_STATUS==="ready"?'<p class="hint" style="margin:12px 0">اطلاعات '+MT_OSM_PEAKS.length+' قلهٔ تکمیلی از © OpenStreetMap contributors (Geofabrik) بارگذاری شده؛ ارتفاع‌های ele برچسب‌گذاری کاربران‌اند و با DEM تأیید نشده‌اند.</p>':''); mtWire();''','mountain attribution')
idx=once(idx, """if(q&&!mtCoord(q)) L=L.filter(p=>(p[1]+" "+p[2]).includes(q)); return mtSort(L); }""", """if(q&&!mtCoord(q)){const canon=t=>String(t||'').replace(/[\u200c\u200d]/g,' ').replace(/ي/g,'ی').replace(/ك/g,'ک').replace(/\s+/g,' ').trim().toLowerCase(); const needle=canon(q); L=L.filter(p=>canon(p[1]+' '+p[2]).includes(needle));} return mtSort(L); }""", 'mountain normalized Persian search')
out.write_text(idx,encoding='utf-8')

s=rain_in.read_text(encoding='utf-8')
anchor=''' for(const ent of entries.values()){
  const result=ms47PrivateCache.get(ent.cacheKey)||{status:'not-found',candidates:[],places:[]};'''
addition=''' // r86: Only run offline OSM place lookup when no *verified* station is available.
 // OSM coordinates are geographic references, never source-verified sensor locations.
 const ms86Osm=new Map();
 const ms86Find=[...entries.values()].filter(ent=>{
   const x=ms47PrivateCache.get(ent.cacheKey)||{};
   return !(x.candidates||[]).some(st=>ms48SafeStation(st,{province:ent.query.province})&&Number(st.score||0)>=.999);
 });
 for(let pos=0;pos<ms86Find.length;pos+=40){
   const batch=ms86Find.slice(pos,pos+40);
   try{
     const rr=await fetch('osm_place_lookup_v86.php?v=86',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({queries:batch.map(b=>({name:b.query.name,province:b.query.province,county:b.query.county}))})});
     if(!rr.ok)continue;
     const jj=await rr.json();if(!jj.ok||!Array.isArray(jj.results)||jj.results.length!==batch.length)continue;
     batch.forEach((b,k)=>ms86Osm.set(b.cacheKey,jj.results[k].status==='ambiguous-truncated'?[]:(jj.results[k].places||[])));
   }catch(e){console.warn('OSM location fallback not available',e.message);break;}
 }
 for(const ent of entries.values()){
  const result=ms47PrivateCache.get(ent.cacheKey)||{status:'not-found',candidates:[],places:[]};
  if(ms86Osm.has(ent.cacheKey))result.places=[...(result.places||[]),...ms86Osm.get(ent.cacheKey)];'''
s=once(s,anchor,addition,'isohyet lookup extension')
anchor='''function ms48ChooseDefault(rec){'''
helper='''/* r86: geographic fallback needs an exact OSM name AND a single locality in
 * the given administrative area; no OSM coordinate is verified as a rain gauge.
 * The polygon comes from the same GIS boundaries that draw the isohyet map. */
function ms86GeoFallback(rec){
 if(!rec||!Array.isArray(rec.candidates)||!rec.name)return null;
 const candidate=rec.candidates.filter(c=>String(c.id||'').startsWith('osm-node-')&&validCoord(c)&&
  ['settlement','agricultural'].includes(c.geographic_category)&&
  (key(c.fa)===key(rec.name)||key(c.name)===key(rec.name)));
 if(!candidate.length)return null;
 const province=ms47LookupProvince(rec);
 const regionPoly=province?regions.find(g=>g.id.startsWith('p:')&&key(g.name)===key(province)):null;
 if(province&&!regionPoly)return null; // cannot validate province without GIS layer
 const eligible=regionPoly?candidate.filter(c=>polyInside([+c.lon,+c.lat],regionPoly.poly)):candidate;
 // If county boundaries are available, respect them too; missing county polygon does not imply a match.
 let filtered=eligible;
 if(rec.county){
   const L=window.CQC_LAYERS||(typeof LAYERS!=='undefined'?LAYERS:(window.parent?.CQC_LAYERS||{}));
   const all=L.shahrestan||L.county||[];
   if(all.length){const shape=all.find(x=>key(x.p?.name||x.name||'')===key(rec.county)&&(!province||!x.p?.ostan||key(x.p.ostan)===key(province)));
     if(shape?.g)filtered=filtered.filter(c=>polyInside([+c.lon,+c.lat],shape.g));
     else return null;}
 }
 const distinct=[];
 for(const c of filtered){
   // duplicate OSM nodes within 600 m represent the same named locality
   if(!distinct.some(x=>Math.hypot((+x.lat-(+c.lat))*111.2,(+x.lon-(+c.lon))*111.2*Math.cos((+x.lat)*Math.PI/180))<.6))distinct.push(c);
 }
 if(distinct.length!==1||filtered.length>25)return null;
 // Any other source claiming the same exact toponym at a conflicting location makes this ambiguous.
 const other=rec.candidates.filter(c=>!String(c.id||'').startsWith('osm-node-')&&c.approximate&&validCoord(c)&&key(c.fa)===key(rec.name));
 if(other.some(c=>Math.hypot((+c.lat-(+distinct[0].lat))*111.2,(+c.lon-(+distinct[0].lon))*111.2*Math.cos(+c.lat*Math.PI/180))>2))return null;
 return distinct[0];
}
function ms48ChooseDefault(rec){'''
s=once(s,anchor,helper,'isohyet geofence helper')
anchor='''  if(rec.candidates.length){rec.match='review';rec.needsReview=true;rec.lat='';rec.lon='';continue;}'''
addition='''  const osm=ms86GeoFallback(rec);
  if(osm){rec.lat=+osm.lat;rec.lon=+osm.lon;rec.elev=osm.elev??null;
   rec.selectedId=osm.id;rec.matchedName=osm.fa;rec.stationType='geographic_reference';
   rec.match='osm-geographic-fallback';rec.locationStatus='osm-toponym-centroid';
   rec.osmSourceUrl=osm.osm_url;rec.geometrySource='OpenStreetMap node (not sensor location)';
   rec.approximate=true;rec.needsReview=false;rec.score=0;continue;}
  if(rec.candidates.length){rec.match='review';rec.needsReview=true;rec.lat='';rec.lon='';continue;}'''
s=once(s,anchor,addition,'isohyet auto-gis fallback')
anchor='''  meta.textContent=r.excluded?'از نقشه کنار گذاشته شد':validCoord(r)&&!r.needsReview?('✓ '+'''
s=once(s,anchor,'''  meta.textContent=r.match==='osm-geographic-fallback'?'◉ موقعیت خودکار نام جغرافیایی از OSM؛ مختصات ابزار هواشناسی تأیید نشده | '+(+r.lat).toFixed(4)+'، '+(+r.lon).toFixed(4):r.excluded?'از نقشه کنار گذاشته شد':validCoord(r)&&!r.needsReview?('✓ '+''','isohyet visible provenance')
s=once(s,"?'geographic-reference-manual':r.match", "?(r.match==='osm-geographic-fallback'?'geographic-reference-auto':'geographic-reference-manual'):r.match",'isohyet CSV status')
s=once(s,"station_type_evidence:r.stationTypeEvidence||'',source:r.source||'user'", "station_type_evidence:r.stationTypeEvidence||'',geometry_source:r.geometrySource||'',osm_source_url:r.osmSourceUrl||'',source:r.source||'user'",'isohyet CSV data')
s=once(s,"'station_type','station_type_status','station_type_evidence']", "'station_type','station_type_status','station_type_evidence','place_approximate','geometry_source','osm_source_url']",'isohyet CSV headers')
# Add actual table web view no change to user approval flow. JS checks escape/markup in existing table.
rain_out.write_text(s,encoding='utf-8')
print('INDEX',len(idx),'rain',len(s),'source_shas',hashlib.sha256(base.read_bytes()).hexdigest(),hashlib.sha256(rain_in.read_bytes()).hexdigest())
