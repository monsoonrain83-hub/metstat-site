/* MetStat V75: only explicit province markers may split a station name. */
(function(root){'use strict';
 function markedScope(name, provinces, normalize){
  const raw=String(name||'').trim();
  const m=raw.match(/^(.*?)\s+استان\s+(.+)$/u)||raw.match(/^(.*?)\s*[-–—،,]\s*(.+)$/u);
  if(!m||!m[1].trim())return {name:raw,province:''};
  const p=provinces.find(x=>normalize(x)===normalize(m[2]));
  return p?{name:m[1].trim(),province:p}:{name:raw,province:''};
 }
 const api=Object.freeze({markedScope});
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.MetStatRainNameScopeV75=api;
})(typeof globalThis!=='undefined'?globalThis:this);
