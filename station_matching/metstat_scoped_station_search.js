/* MetStat scoped station matching guard. No network calls or map side effects. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;else root.MetStatScopedStationSearch=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const normalize=s=>String(s??"").normalize("NFKC").replace(/[يى]/g,"ی").replace(/ك/g,"ک").replace(/[\u200c\u200d]/g," ").replace(/[ًٌٍَُِّْ]/g,"").replace(/[-_]+/g," ").replace(/\s+/g," ").trim().toLocaleLowerCase("fa");
const list=v=>Array.isArray(v)?v:[];
function parse(text){const raw=String(text??"").trim();const sep=raw.match(/^([^:：]+)\s*[:：]\s*(.+)$/);return sep?{place:normalize(sep[1]),station:normalize(sep[2])}:{place:"",station:normalize(raw)};}
function scope(records,provinces){const allowed=new Set(list(provinces).map(normalize).filter(Boolean));return !allowed.size?list(records):list(records).filter(r=>allowed.has(normalize(r.province||r.ostan)));}
function candidates(records,input,opts={}){
 const {place,station}=parse(input);const allowed=scope(records,opts.provinces);const result=[];
 for(const r of allowed){
  const names=[r.name_fa,r.name,r.name_en,...list(r.aliases)].map(normalize).filter(Boolean);
  const province=normalize(r.province||r.ostan),county=normalize(r.county||r.shahrestan),city=normalize(r.city);
  if(place && ![county,city,province].some(v=>v&&v===place))continue;
  const exact=names.includes(station),partial=!exact&&station.length>=4&&names.some(n=>n.includes(station)||station.includes(n));
  if(!exact&&!partial)continue;
  const lat=Number(r.lat),lon=Number(r.lon);
  const hasCoordinates=r.lat!==""&&r.lat!=null&&r.lon!==""&&r.lon!=null&&Number.isFinite(lat)&&Number.isFinite(lon)&&lat>=-90&&lat<=90&&lon>=-180&&lon<=180;
  result.push({record:r,score:(exact?100:50)+(place?20:0)+(hasCoordinates?10:0),exact,hasCoordinates});
 }
 return result.sort((a,b)=>b.score-a.score);
}
function resolve(records,input,opts={}){
 const matches=candidates(records,input,opts),valid=matches.filter(x=>x.exact&&x.hasCoordinates);
 if(valid.length===1 && (matches.length===1||valid[0].score>matches[1].score))return {status:"confirmed",match:valid[0].record,candidates:matches};
 return {status:matches.length?"review":"unresolved",match:null,candidates:matches};
}
return {normalize,parse,scope,candidates,resolve};
});
