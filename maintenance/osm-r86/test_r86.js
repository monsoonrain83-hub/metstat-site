/* Integration-oriented tests of extracted production JS blocks without modifying user data. */
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname;
const source=fs.readFileSync(root+'/index_r86.html','utf8');
const rain=fs.readFileSync(root+'/station_isohyet_r86.html','utf8');
const peakData=JSON.parse(fs.readFileSync(root+'/mountain_peaks_osm_v86.json','utf8'));
function portion(src,start,end){const a=src.indexOf(start),b=src.indexOf(end,a+start.length);assert(a>=0&&b>a,'missing anchors: '+start);return src.slice(a,b)}
const mountain=portion(source,'/* r86: OSM named peaks','/* r91: مکان‌یابی استان/شهرستان/حوضه');
const peakContext={MT_PEAKS:[['damavand','دماوند','Damavand',35.954365,52.11034,5609,'ir']],MT_EXTRA:[],MT_NEW:[],MT_WORLD:[],MT:{my:[]},fetch:async()=>({ok:true,json:async()=>peakData}),console,Math};
vm.createContext(peakContext);vm.runInContext(mountain+';globalThis.testMountain={load:mtLoadOsmPeaks,all:mtAll,count:()=>MT_OSM_PEAKS.length,status:()=>MT_OSM_STATUS,escape:mtOsmEsc};',peakContext,{timeout:6000});
function asJson(v){return JSON.parse(JSON.stringify(v))}
(async()=>{
 const n=await peakContext.testMountain.load();assert(n>=2200&&n<2304);assert.strictEqual(peakContext.testMountain.status(),'ready');
 const a=peakContext.testMountain.all();assert.strictEqual(a.length,n+1);assert.strictEqual(a.filter(x=>x[1]==='دماوند').length,1);
 assert.strictEqual(peakContext.testMountain.escape('<img onerror="x">'),'&lt;img onerror=&quot;x&quot;&gt;');
 const gf=portion(rain,'/* r86: geographic fallback','function ms48ChooseDefault');
 const province={id:'p:گیلان',name:'گیلان',poly:[[[[48.5,36.5],[51,36.5],[51,38.5],[48.5,38.5],[48.5,36.5]]]]};
 const T={regions:[province],window:{CQC_LAYERS:{}},ms47LookupProvince:r=>r.province,key:x=>String(x||'').trim().replace(/\u200c/g,' '),
   validCoord:x=>Number.isFinite(+x.lat)&&Number.isFinite(+x.lon)&&+x.lat>0&&+x.lon>0,
   polyInside:(p,polys)=>{let inside=false;for(const poly of polys){for(const ring of poly){let s=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])s=!s}if(s)inside=true;}}return inside},Math};
 vm.createContext(T);vm.runInContext(gf+';globalThis.geotest=ms86GeoFallback;',T,{timeout:3000});
 const g={id:'osm-node-123',name:'امامزاده اسحاق',fa:'امامزاده اسحاق',lat:37.0516,lon:49.32286,geographic_category:'settlement',approximate:true};
 const rec={name:g.name,province:'گیلان',candidates:[g]};assert.strictEqual(T.geotest(rec).id,g.id);
 assert.strictEqual(T.geotest({...rec,province:'تهران'}),null);
 assert.strictEqual(T.geotest({...rec,candidates:[g,{...g,id:'osm-node-124',lat:37.7,lon:50.7}]}),null);
 assert.strictEqual(T.geotest({...rec,candidates:[g,{...g,id:'osm-node-124',lat:37.0517,lon:49.3229}]}).id,g.id);
 assert.strictEqual(T.geotest({...rec,candidates:[g,{id:'oldgeo',fa:g.name,lat:36.1,lon:49.4,approximate:true}]}),null);
 assert.strictEqual(T.geotest({...rec,candidates:[{...g,fa:'ایستگاه دیگر',name:'ایستگاه دیگر'}]}),null);
 const result={mountain_osm_added:n,mountain_duplicate_prevented:true,mountain_html_escape:true,province_and_ambiguity_guard_tests:6,passed:10};
 console.log(JSON.stringify(result,null,2));fs.writeFileSync(root+'/JS_unit_results_v86.json',JSON.stringify(result,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
