"""Create candidate custom-route patch from the verified live R5 frontend; no deployment."""
from pathlib import Path
import hashlib,json,zipfile
BASE=Path("r5-candidate")
archive=Path("metstat-r5-live-20261124.zip")
assert hashlib.sha256(archive.read_bytes()).hexdigest()=="3f045718ad311d23a120e7fb5ecf4c5e3a0b49cbdfbbf14ab49e6e2143b22ab3"
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist())==26 and all(n=="index.html" or (n.startswith("assets/") and n.count("/")==1 and ".." not in n) for n in z.namelist())
    z.extractall(BASE)
index=BASE/"index.html"
s=index.read_text()
core=BASE/"assets/ms_r5_perf_core_ddee74fdbe848c59.js"
c=core.read_text()
routes={'isohyet':'/monitoring-forecast/station-isohyet','verify-forecast':'/monitoring-forecast/forecast-verification','bulletin-maps':'/monitoring-forecast/bulletin-maps','toolbox-full':'/meteorological-toolbox','convert-unit':'/meteorological-toolbox/unit-converter','toolbox-spatial':'/meteorological-toolbox/station-idw','convert-weather':'/meteorological-toolbox/weather-file-converter','convert-media':'/meteorological-toolbox/media-converter','convert-document':'/meteorological-toolbox/document-converter','ava-voice':'/ava-studio/voice','ava-video':'/ava-studio/video','ava-photo':'/ava-studio/photo','ava-lightning':'/ava-studio/lightning'}
def replace(s,a,b):
    assert s.count(a)==1,(a[:150],s.count(a))
    return s.replace(a,b,1)
registry='''<script id="ms-r5-custom-route-registry">(function(){'use strict';
 const paths=Object.freeze(%s);
 const enabled=new URLSearchParams(location.search).get('ms_ui_legacy')!=='1';
 function current(){if(!enabled)return '';const p=location.pathname.replace(/\\/+$/,'')||'/';const h=location.hash.replace(/^#\\/?/,'/').replace(/\\/+$/,'');return Object.keys(paths).find(k=>paths[k]===h||paths[k]===p)||'';}
 window.MS_R5_CUSTOM_ROUTE={paths,current,active:!!current()};
})();</script>\n'''%json.dumps(routes,separators=(',',':'))
ref=f'<script src="/assets/{core.name}">'
s=replace(s,ref,registry+ref)
c=replace(c,'function setRoute(mode,replace){\n  try{','function setRoute(mode,replace){\n  if(window.MS_R5_CUSTOM_ROUTE?.active)return;\n  try{')
c=replace(c,'window.addEventListener("popstate", ()=>{ V.nav=true; try{ openMode(routeOf()); } finally{ V.nav=false; } });','''window.addEventListener("popstate", ()=>{ const r=window.MS_R5_CUSTOM_ROUTE; if(r){r.active=!!r.current();if(r.active)return;window.MetStatR7?.clearCustom?.();} V.nav=true; try{ openMode(routeOf()); } finally{ V.nav=false; } });''')
s=replace(s," function legacy(action){\n  document.body.classList.remove('ms7-custom');if(custom){custom.querySelector('[data-ms22-converter]')?.dispatchEvent(new Event('ms22-dispose'));custom.hidden=true;custom.replaceChildren()}",""" function clearCustom(){
  window.MS_R5_CUSTOM_ROUTE.active=false;
  document.body.classList.remove('ms7-custom');if(custom){custom.querySelector('[data-ms22-converter]')?.dispatchEvent(new Event('ms22-dispose'));custom.hidden=true;custom.replaceChildren()}
 }
 function legacy(action){
  const leaving=window.MS_R5_CUSTOM_ROUTE.active;clearCustom();""")
s=replace(s,"if(typeof window.shellGo==='function'){window.shellGo(action);return true}","if(typeof window.shellGo==='function'){window.shellGo(action);if(leaving&&typeof setRoute==='function'&&typeof anRouteKey==='function'&&typeof store!=='undefined'){const mode=store.get('mode','');if(mode)setRoute(anRouteKey(mode));}return true}")
s=replace(s,' function navigate(dest,label){close();lastRoute=dest;applyTitle(label);markCurrent(dest);',""" function navigate(dest,label,fromHistory=false){close();lastRoute=dest;applyTitle(label);markCurrent(dest);
  const router=window.MS_R5_CUSTOM_ROUTE;
  if(Object.prototype.hasOwnProperty.call(router.paths,dest)){
   router.active=true;
   if(!fromHistory){const path=router.paths[dest];const target=(typeof ROUTE_PATH!=='undefined'&&ROUTE_PATH)?path+location.search:'/index.html'+location.search+'#'+path;
    if(location.pathname+location.search+location.hash!==target)history.pushState({msR5Custom:dest},'',target);}
  }""")
s=replace(s,"    badgeModel();\n   }catch(e){console.error('MetStat r7 shell init:',e)}}","""    badgeModel();
    const restoreCustom=()=>{const dest=window.MS_R5_CUSTOM_ROUTE.current();if(!dest)return;
     const item=NAV.flatMap(g=>g[3]).find(x=>x[1]===dest);if(item)navigate(dest,item[0],true);};
    window.addEventListener('popstate',restoreCustom);restoreCustom();
   }catch(e){console.error('MetStat r7 shell init:',e)}}""")
s=replace(s,'window.MetStatR7=Object.freeze({navigate,menu:', 'window.MetStatR7=Object.freeze({navigate,clearCustom,menu:')
newcore='ms_r5_perf_core_'+hashlib.sha256(c.encode()).hexdigest()[:16]+'.js'
s=replace(s,ref,f'<script src="/assets/{newcore}">')
index.write_text(s)
(BASE/'assets'/newcore).write_text(c)
Path('r5-custom-routes.json').write_text(json.dumps(routes,indent=2))
print(newcore, len(routes))
# Candidate must match the locally prepared exact frontend files.
assert newcore=="ms_r5_perf_core_5bf9868a04910eee.js"
