/* Parser for Persian station-precipitation reports, preserving source order/labels. */
(function(root, factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatRainParser=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 function faDigits(s){return String(s).replace(/[۰-۹]/g,x=>String('۰۱۲۳۴۵۶۷۸۹'.indexOf(x))).replace(/[٠-٩]/g,x=>String('٠١٢٣٤٥٦٧٨٩'.indexOf(x)));}
 function parseRainReport(text){
   const textLines=String(text).split(/\r?\n/);const header=textLines.slice(0,6).join(' ');
   const pm=header.match(/(?:استان|هواشناسی)\s+([آ-ی]+)(?=[\s\u00a0]|$)/u);
   const province=pm?pm[1]:'';
   const dates=[...header.matchAll(/[۰-۹٠-٩0-9]{4}\/[۰-۹٠-٩0-9]{1,2}\/[۰-۹٠-٩0-9]{1,2}/g)].map(m=>m[0]);
   const reportDate=dates.length>=2 ? dates[0]+' تا '+dates[dates.length-1] : (dates[0]||'');
   const rows=[],rejected=[];
   for(let i=0;i<textLines.length;i++){
     const src=textLines[i].trim().replace(/\u00a0/g,' ');
     // Only bullet-prefixed data lines, not dates in title or totals in prose.
     if(!/^[🔸🔹•●▪\-*]\s*/u.test(src))continue;
     let clean=src.replace(/^[🔸🔹•●▪\-*]+\s*/u,'').replace(/^#/u,'').trim();
     clean=clean.replace(/^[\s#]+/u,'').replace(/_/g,' ').trim();
     // Arabic/Persian digits glued to the place name are separated here.
     const m=clean.match(/^(.+?)\s*([۰-۹٠-٩0-9]+[\/٫.][۰-۹٠-٩0-9]+|[۰-۹٠-٩0-9]+)\s*(?:میلی\s*متر|mm)?\s*$/u);
     if(!m){rejected.push({line:i+1,text:src});continue;}
     const name=m[1].replace(/[\s#]+$/,'').trim();
     let raw=faDigits(m[2]).replace(/[\/٫]/g,'.');const amount=Number(raw);
     if(!name||!Number.isFinite(amount)||amount<0||amount>3000){rejected.push({line:i+1,text:src});continue;}
     rows.push({name,province,precip_mm:amount,source_line:i+1,raw_name:m[1]});
   }
   return {rows,rejected,province,reportDate,count:rows.length};
 }
 return Object.freeze({faDigits,parseRainReport});
});
