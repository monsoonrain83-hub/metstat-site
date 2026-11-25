/* Conservative station-name preprocessor for rainfall QC.
 * Never substitutes a district name for a station name or accepts a fuzzy
 * match without verified geographic coordinates and province context. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatStationQC=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function norm(s){return String(s||'').normalize('NFKC').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/[\u200c\u200d]/g,' ').replace(/[ًٌٍَُِّْ]/g,'').replace(/[ـ]/g,'').replace(/\s+/g,' ').trim();}
function validCoords(c){
 const numeric=v=>(typeof v==='number'||(typeof v==='string'&&v.trim()!==''))&&Number.isFinite(Number(v));
 return numeric(c?.lat)&&numeric(c?.lon)&&Number(c.lat)>=24&&Number(c.lat)<=41&&Number(c.lon)>=43&&Number(c.lon)<=64;
}
function parse(name){const parts=norm(name).split(/\s*[:：]\s*/);return {station:parts.length>1?parts.slice(1).join(':').trim():parts[0],district:parts.length>1?parts[0]:null,original:name};}
function eligible(input,candidate,options={}){const p=parse(input);const target=norm(candidate?.name);if(!target||!p.station||target!==p.station)return {ok:false,reason:'not_exact_station'};if(!validCoords(candidate))return {ok:false,reason:'unverified_coordinates'};if(!norm(candidate?.province))return {ok:false,reason:'missing_province'};if(p.district&&norm(candidate?.district)!==p.district)return {ok:false,reason:'district_mismatch'};if(options.province&&norm(candidate.province)!==norm(options.province))return {ok:false,reason:'province_mismatch'};return {ok:true,reason:'exact_with_location'};}
function choose(input,candidates,options={}){
 const ranked=[];
 for(const c of candidates||[]){
  if(!c)continue;
  const names=[c.name,...(Array.isArray(c.aliases)?c.aliases:[])];
  for(const alias of names){
   const probe=eligible(input,{...c,name:alias},options);
   if(probe.ok){ranked.push({candidate:c,matchedName:alias});break;}
  }
 }
 // Even a perfect normalized alias must not auto-resolve to two stations.
 if(ranked.length!==1)return {ok:false,reason:ranked.length?'ambiguous_georeferenced_candidates':'no_verified_candidate',candidates:ranked.length};
 return {ok:true,reason:'unique_verified_alias',candidate:ranked[0].candidate};
}
return {norm,parse,eligible,choose};
});
