/* Orchestrates report import: parse -> admin gazetteer -> station priority -> geocode -> UI.
 * Adapter to legacy MetStat v59+ must supply getStations (existing decoded DB/API),
 * mapLayer renderer and optionally a Leaflet instance for map controls.
 */
(function(root,factory){const api=factory(root);if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatAutoFlow=api;})(typeof globalThis!=='undefined'?globalThis:this,function(root){
'use strict';
const norm=(s)=>root.MetStatAutoMatch?.normalize(s)||String(s||'').trim();
async function json(url){const r=await fetch(url,{credentials:'same-origin'});if(!r.ok)throw new Error('gazetteer:'+r.status);return r.json();}
async function loadPlaces(provinces,base='/online/data/iran_places'){
 const index=await json(base+'/provinces.json'); const ids=Object.entries(index).filter(([,p])=>provinces.some(v=>norm(p)===norm(v))).map(([id])=>id);
 const shards=await Promise.all(ids.map(id=>json(base+'/p_'+id+'.json')));
 return shards.flatMap(shard=>Object.values(shard.names).flatMap(g=>g.map(p=>({...p,province:shard.province}))));
}
function makeGeocoder(endpoint='/online/api/metstat_location_lookup.php'){
 return async function (query){
  const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(query),credentials:'same-origin'});
  const body=await response.json();if(!response.ok&&body.status!=='ambiguous')throw new Error(body.reason||'HTTP '+response.status);return body;
 };
}
/** Process all 46 or N entries with no manual step unless every lookup fails or is ambiguous. */
async function processReport(reportText,opts){
 const P=root.MetStatRainParser,M=root.MetStatAutoMatch;
 if(!P||!M)throw new Error('load parser and auto matcher first');
 if(typeof opts?.getStations!=='function')throw new Error('Must wire the current v59+ station bank via getStations');
 const parsed=P.parseRainReport(reportText);if(parsed.count===0)throw new Error('هیچ رکورد بارشی در گزارش شناخته نشد');
 const stations=await opts.getStations(parsed.rows);
 if(!Array.isArray(stations))throw new Error('Existing station lookup did not return an array');
 let places=[];try{places=await loadPlaces([...new Set(parsed.rows.map(r=>r.province).filter(Boolean))],opts.placesBase);}catch(e){opts.onNotice?.('مرجع تقسیمات کشوری بارگذاری نشد؛ جست‌وجوی خارجی ادامه دارد.');}
 const geocode=opts.geocode||makeGeocoder(opts.geocodeEndpoint);
 const result=await M.resolveBatch(parsed.rows,stations,{places,province:parsed.province,geocode,onProgress:opts.onProgress});
 const all={...result,parsed,rejected:parsed.rejected};
 if(opts.mapTools?.updateCounts)opts.mapTools.updateCounts(result.counts);
 if(opts.mapTools?.setMetadata)opts.mapTools.setMetadata({title:'گزارش بارش ایستگاه‌های هواشناسی '+parsed.province,reportDate:parsed.reportDate,province:parsed.province});
 opts.onComplete?.(all);
 // All mapped locations are passed together; the existing UI should not require 10 station selections.
 opts.renderMapped?.(result.records.filter(r=>r.chosen));
 opts.renderReview?.(result.records.filter(r=>!r.chosen));
 return all;
}
return Object.freeze({loadPlaces,makeGeocoder,processReport});
});
