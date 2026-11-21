/* User-confirmed rainfall station corrections (same browser, no cross-province leakage). */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatStationCorrections=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const norm=s=>String(s||'').normalize('NFKC').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/[\u200c\u200d]/g,' ').replace(/\s+/g,' ').trim().toLowerCase();
function cache({storage,key='metstat.rain.stationCorrections.v1'}){
 if(!storage)throw Error('storage required');
 function load(){try{const x=JSON.parse(storage.getItem(key)||'{}');return x&&typeof x==='object'&&!Array.isArray(x)?x:{};}catch(_e){return {};}}
 function makeKey(input,provinces=[]){return norm(input)+'|'+[...new Set(provinces.map(norm))].sort().join(',');}
 function remember(input,station,provinces=[]){
  const id=String(station?.id||'');
  const lat=Number(station?.lat),lon=Number(station?.lon);
  if(!id||!station?.name_fa||station?.lat==null||station?.lon==null||!Number.isFinite(lat)||!Number.isFinite(lon)||lat<24||lat>41||lon<43||lon>64)return false;
  if(provinces.length&&!provinces.map(norm).includes(norm(station.province)))return false;
  const data=load(),k=makeKey(input,provinces);
  data[k]={id,lat,lon,province:norm(station.province),checked:true};
  try{storage.setItem(key,JSON.stringify(data));return true;}catch(_e){return false;}
 }
 function recall(input,candidates,provinces=[]){
  const saved=load()[makeKey(input,provinces)];
  if(!saved?.checked)return null;
  return (candidates||[]).find(s=>String(s.id)===saved.id&&norm(s.province)===saved.province&&Number(s.lat)===saved.lat&&Number(s.lon)===saved.lon&&(!provinces.length||provinces.map(norm).includes(norm(s.province))))||null;
 }
 function exportCorrections(){return load();}
 return {remember,recall,exportCorrections};
}
return {cache,norm};
});
