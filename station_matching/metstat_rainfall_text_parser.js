/* Interpret Persian rainfall text before station search. Never emit coordinates. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatRainText=api;}
)(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function clean(s){return String(s||'').normalize('NFKC').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/[\u200c\u200d]/g,' ').replace(/[\u0660-\u0669]/g,c=>String(c.charCodeAt(0)-0x660)).replace(/[\u06f0-\u06f9]/g,c=>String(c.charCodeAt(0)-0x6f0)).replace(/٫/g,'.').replace(/\s+/g,' ').trim();}
const units={صفر:0,یک:1,دو:2,سه:3,چهار:4,پنج:5,شش:6,هفت:7,هشت:8,نه:9,ده:10,یازده:11,دوازده:12,سیزده:13,چهارده:14,پانزده:15,شانزده:16,هفده:17,هجده:18,نوزده:19,بیست:20,سی:30,چهل:40,پنجاه:50,شصت:60,هفتاد:70,هشتاد:80,نود:90,صد:100,دویست:200,سیصد:300,چهارصد:400,پانصد:500,ششصد:600,هفتصد:700,هشتصد:800,نهصد:900,هزار:1000};
function wordNumber(s){const v=clean(s).split(/\s+و\s+|\s+/).filter(Boolean);if(!v.length||v.some(w=>units[w]===undefined))return null;let sum=0;for(const w of v){if(w==='هزار')sum=Math.max(1,sum)*1000;else sum+=units[w];}return sum;}
function splitRecord(raw){let line=clean(raw).replace(/\s*(?:میلی\s*متر|mm)\s*$/i,'').trim();if(!line)return null;
 let m=line.match(/^(.*?)\s+([+-]?\d+(?:[.,]\d+)?)$/);
 if(m)return {name:m[1].trim().replace(/[،,:：]+$/,'').trim(),amount:mm(m[2])};
 // Small, unambiguous Persian number phrases: prefer longest suffix.
 let tok=line.split(' ');
 for(let n=Math.min(5,tok.length-1);n>=1;n--){let suffix=tok.slice(-n).join(' ');let value=wordNumber(suffix);if(value!==null)return {name:tok.slice(0,-n).join(' ').trim(),amount:value};}
 return null;
}
function mm(s){const n=Number(String(s).replace(',','.'));return Number.isFinite(n)&&n>=0&&n<=3000?n:null;}
function parse(text){let rows=[],errors=[];let lines=String(text||'').split(/[\r\n;؛]+/);
 for(let i=0;i<lines.length;i++){const raw=lines[i].trim();if(!raw)continue;const rec=splitRecord(raw);
 if(rec&&rec.name&&rec.amount!==null){rows.push({...rec,line:i+1,original:raw});}
 else errors.push({line:i+1,original:raw,reason:'not_a_rainfall_measurement'});}
 return {rows,errors};
}
function resolveText(text,stationRecords,search,selectedProvinces=[]){
 if(!search||typeof search.resolve!=='function')throw Error('search.resolve required');
 const norm=search.normalize||clean;
 const knownProvinces=[...new Set((stationRecords||[]).map(r=>clean(r.province||r.ostan)).filter(Boolean))].sort((a,b)=>b.length-a.length);
 const knownCities=[...new Set((stationRecords||[]).map(r=>clean(r.city||r.county)).filter(Boolean))].sort((a,b)=>b.length-a.length);
 const chosen=selectedProvinces.map(norm);let province='',city='',results=[],errors=[];
 const lines=String(text||'').split(/[\\r\\n;؛]+/);
 for(let i=0;i<lines.length;i++){
  const original=lines[i].trim();if(!original)continue;const line=clean(original);
  const prov=knownProvinces.find(p=>line.includes('استان '+p));
  if(prov && !splitRecord(original)){province=prov;city='';continue;}
  const ct=knownCities.find(x=>line.includes('شهر '+x));
  if(ct && !splitRecord(original)){city=ct;continue;}
  const rec=splitRecord(original);
  if(!rec||!rec.name||rec.amount===null){errors.push({line:i+1,original,reason:'not_a_rainfall_measurement'});continue;}
  const effective=province?(chosen.length?chosen.filter(p=>p===norm(province)):[province]):selectedProvinces;
  if(province && chosen.length && !effective.length){results.push({...rec,line:i+1,original,match:{status:'unresolved',reason:'header_outside_selected_provinces'}});continue;}
  const scoped=city?(stationRecords||[]).filter(r=>norm(r.city||r.county)===norm(city)):stationRecords;
  results.push({...rec,line:i+1,original,match:search.resolve(scoped,rec.name,{provinces:effective})});
 }
 return {rows:results.map(({name,amount,line,original})=>({name,amount,line,original})),errors,results};
}
return {clean,parse,splitRecord,wordNumber,resolveText};
});
