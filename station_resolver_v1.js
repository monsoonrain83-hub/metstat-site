/* Station disambiguation with explicit geographic context and persisted decisions.
 * This module never infers coordinates from names and never overrides a verified
 * station identity with a nearby city/place. Pure functions for safe integration. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatStationResolver=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const norm=s=>String(s||'').normalize('NFKC').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/[\u200c\u200d]/g,' ').replace(/ـ/g,'').replace(/\s+/g,' ').trim().toLowerCase();
function validCoords(c){
 const numeric=v=>(typeof v==='number'||(typeof v==='string'&&v.trim()!==''))&&Number.isFinite(Number(v));
 return numeric(c?.lat)&&numeric(c?.lon)&&Number(c.lat)>=24&&Number(c.lat)<=41&&Number(c.lon)>=43&&Number(c.lon)<=64;
}
function parse(text,context={}){
 const raw=norm(text);const p=raw.split(/\s*[:：]\s*/);const station=p.length>1?p.slice(1).join(':').trim():raw;
 return {station,county:p.length>1?p[0]:norm(context.county),province:norm(context.province),city:norm(context.city)};
}
function scopeFromText(text,provinces=[],cities=[]){
 const s=norm(text);let province='',city='';
 for(const p of [...provinces].sort((a,b)=>norm(b).length-norm(a).length)){
  if(s.includes('استان '+norm(p))){province=norm(p);break;}
 }
 for(const t of [...cities].sort((a,b)=>norm(b).length-norm(a).length)){
  if(s.includes('شهر '+norm(t))){city=norm(t);break;}
 }
 return {province,city};
}
function rank(record){const type=norm(record.type||record.network);return /synoptic|سینوپتیک/.test(type)?5:/automatic|خودکار/.test(type)?4:/climatology|اقلیم/.test(type)?3:/raingauge|باران/.test(type)?2:/hydro|هیدرو/.test(type)?2:1;}
function resolve(text,candidates,context={},learned={}){
 const q=parse(text,context);if(!q.station)return {status:'unresolved',reason:'empty_station'};
 const out=[];for(const c of candidates||[]){
  if(!c||!norm(c.province)||!validCoords(c))continue;
  const aliases=[c.nameFa,c.nameEn,...(Array.isArray(c.aliases)?c.aliases:[])].filter(v=>typeof v==='string').map(norm);
  if(!aliases.includes(q.station))continue;
  if(q.province&&norm(c.province)!==q.province)continue;
  if(q.county&&norm(c.county)!==q.county)continue;
  if(q.city&&norm(c.city)!==q.city&&norm(c.county)!==q.city)continue;
  out.push(c);
 }
 const key=[q.province,q.county,q.city,q.station].join('|');
 const selected=Object.prototype.hasOwnProperty.call(learned||{},key)?learned[key]:null;if(selected){const hit=out.find(c=>String(c.id)===String(selected));if(hit)return {status:'verified',reason:'learned_verified_override',candidate:hit,key};}
 if(!out.length)return {status:'unresolved',reason:'no_georeferenced_exact_match',key};
 // Different physical sites with the same name remain ambiguous, even if one
 // is synoptic; only co-located types may be consolidated by priority.
 out.sort((a,b)=>rank(b)-rank(a));const first=out[0];const collocated=out.every(c=>{
  if(norm(c.province)!==norm(first.province))return false;
  const dy=(Number(c.lat)-Number(first.lat))*111;const dx=(Number(c.lon)-Number(first.lon))*111*Math.cos(Number(first.lat)*Math.PI/180);return Math.hypot(dx,dy)<=.3;
 });
 if(out.length>1&&!collocated)return {status:'ambiguous',reason:'multiple_distinct_station_locations',candidates:out,key};
 return {status:'verified',reason:out.length>1?'co_located_priority':'unique_exact',candidate:first,key};
}
return {parse,resolve,norm,scopeFromText};
});
