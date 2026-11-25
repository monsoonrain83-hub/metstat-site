/* Suggestion-only Persian and Latin station search.
 * Never authorizes an automatic station match or invents coordinates.
 * Candidate records must already have a geographic reference. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatStationSuggestions=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const norm=v=>String(v??'').normalize('NFKD').toLowerCase().replace(/\p{M}/gu,'').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/ـ/g,'').replace(/[\u200c\u200d]/g,' ').replace(/[\p{P}\p{Z}\s]+/gu,' ').trim();
const compact=v=>norm(v).replace(/\s/g,'');
const letters=Object.freeze({'ا':'a','ب':'b','پ':'p','ت':'t','ث':'s','ج':'j','چ':'ch','ح':'h','خ':'kh','د':'d','ذ':'z','ر':'r','ز':'z','ژ':'zh','س':'s','ش':'sh','ص':'s','ض':'z','ط':'t','ظ':'z','ع':'','غ':'gh','ف':'f','ق':'gh','ک':'k','گ':'g','ل':'l','م':'m','ن':'n','و':'v','ه':'h','ی':'y','ء':''});
function skeleton(v){
 let s=compact(v).replace(/[\u0621-\u06ff]/g,c=>letters[c]??'');
 return s.replace(/kh/g,'X').replace(/gh|q/g,'Q').replace(/sh/g,'S').replace(/ch/g,'C').replace(/zh/g,'Z').replace(/[aeiouy]/g,'').replace(/v/g,'w').replace(/(.)\1+/g,'$1').toLowerCase();
}
function distance(a,b){
 let row=Array.from({length:b.length+1},(_,j)=>j);
 for(let i=1;i<=a.length;i++){const n=[i];for(let j=1;j<=b.length;j++)n[j]=Math.min(n[j-1]+1,row[j]+1,row[j-1]+(a[i-1]===b[j-1]?0:1));row=n;}
 return row[b.length];
}
const numeric=v=>(typeof v==='number'||(typeof v==='string'&&v.trim()!==''))&&Number.isFinite(Number(v));
function inScope(c,s){
 if(!c||!norm(c.province)||!numeric(c.lat)||!numeric(c.lon)||Number(c.lat)<24||Number(c.lat)>41||Number(c.lon)<43||Number(c.lon)>64)return false;
 if(norm(s.province)&&compact(c.province)!==compact(s.province))return false;
 for(const k of ['county','district'])if(norm(s[k])&&norm(c[k])&&compact(c[k])!==compact(s[k]))return false;
 return true;
}
function score(q,n){
 const a=compact(q),b=compact(n);
 if(!a||!b)return null;
 if(norm(q)===norm(n))return {score:100,reason:'normalized_exact'};
 if(a===b)return {score:96,reason:'spacing_variant'};
 if(Math.min(a.length,b.length)>=5&&/^[a-z]+$/.test(a)===/^[a-z]+$/.test(b)){
  const d=distance(a,b),m=Math.max(a.length,b.length);
  if(d<=Math.min(2,Math.floor(m/5)))return {score:Math.round(90-25*d/m),reason:'spelling_variant'};
 }
 const x=skeleton(a),y=skeleton(b);
 if(x.length>=3&&x===y)return {score:70,reason:'phonetic_candidate'};
 return null;
}
function suggest(input,candidates,scope={},limit=8){
 const raw=norm(input),parts=String(input??'').split(/[:：]/);
 const q=parts.length>1?parts.slice(1).join(':'):raw;
 const ctx={...scope};
 if(parts.length>1){if(ctx.county&&compact(ctx.county)!==compact(parts[0]))return [];ctx.county=parts[0];}
 if(!compact(q)||compact(q).length>100)return [];
 const rows=[];
 for(const c of candidates||[]){
  if(!inScope(c,ctx))continue;
  const names=[c.nameFa,c.nameEn,c.name,...(Array.isArray(c.aliases)?c.aliases:[])].filter(v=>typeof v==='string'&&v.length<=150);
  let best=null;
  for(const name of names){const hit=score(q,name);if(hit&&(!best||hit.score>best.score))best={...hit,matchedName:name};}
  if(best){
   const missingContext=['county','district'].filter(k=>norm(ctx[k])&&!norm(c[k]));
   const matchScore=best.score;
   rows.push({candidate:c,...best,matchScore,score:matchScore-(missingContext.length?15:0),missingContext,requiresConfirmation:true});
  }
 }
 rows.sort((a,b)=>b.score-a.score||String(a.candidate.id??'').localeCompare(String(b.candidate.id??'')));
 const topScore=rows[0]?.score;const topTieCount=rows.filter(r=>r.score===topScore).length;
 return rows.slice(0,Math.max(0,Math.min(30,Number.isFinite(limit)?Math.floor(limit):8))).map(r=>({...r,topTieCount,ambiguousTop:r.score===topScore&&topTieCount>1}));
}
return Object.freeze({norm,compact,skeleton,suggest});
});
