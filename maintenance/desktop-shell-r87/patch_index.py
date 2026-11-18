#!/usr/bin/env python3
"""Conservative source-anchored MetStat desktop-shell and OSM overlay patch."""
from pathlib import Path
import hashlib,sys,re
base=Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/metstat_r86_work/index_r86.html')
out=Path(sys.argv[2] if len(sys.argv)>2 else '/mnt/data/metstat_r87_work/public/index.html')
s=base.read_text(encoding='utf-8')
old_hash='6f735fe0c75766d9b997be65c361218f3142c680ba47be8db717250d1992c18c'
if hashlib.sha256(s.encode()).hexdigest()!=old_hash:raise RuntimeError('Source is not the reviewed r86 index. Stop instead of applying patch to unknown host. SHA='+hashlib.sha256(s.encode()).hexdigest())
def one(a,b,why):
 global s
 count=s.count(a)
 if count!=1:raise RuntimeError(f'{why}: expected 1, got {count} for {a[:80]!r}')
 s=s.replace(a,b,1)

one('<meta name="viewport" content="width=device-width, initial-scale=1">','<meta name="viewport" content="width=1360, user-scalable=yes">','desktop viewport mobile')
one("var desktop='width=device-width, initial-scale=1, user-scalable=yes', full='width=device-width, initial-scale=1, user-scalable=yes';","var desktop='width=1360, user-scalable=yes', full='width=1360, user-scalable=yes';",'p8 overwrites viewport')
# Existing zoom-on-desktop-in-mobile zoom hack breaks the desktop composition. Keep zoom at 1.
one('if(touch && sw<=700 && iw>=760){ var z=Math.max(1.4,Math.min(2.0,iw/sw*0.7)); document.documentElement.style.zoom=String(+z.toFixed(2)); document.documentElement.className+=" dskPhone"; }','if(touch && sw<=700 && iw>=760){ document.documentElement.style.zoom="1"; document.documentElement.className+=" dskPhone"; }','remove double zoom')
# Existing fallback on narrow windows returns actual tool controls to image. Desktop view must not do this.
one('if(window.innerWidth<1000){restore(r);restore(nm);if(t){Array.from(t.children).forEach(restore);}return;}','/* Desktop shell at all viewports; do not move page controls back into the map. */','p8 small viewport move')
# The presentation stages are determined by the region's longitude span, not device width.
one('GEO_TC=["#c81e1e","#111","#1d4ed8","#8a5a1c"], GEO_TT=["#8b1010","#111","#1e3a8a","#5b3a0f"]','GEO_TC=["#c81e1e","#111","#1d4ed8","#15817f"], GEO_TT=["#8b1010","#111","#1e3a8a","#13504f"]','village marker color')
one('} else if(t===3){ x.moveTo(X,Y-r*1.2); x.lineTo(X+r*1.1,Y+r*.8); x.lineTo(X-r*1.1,Y+r*.8); x.closePath(); } else x.arc(X,Y,r,0,6.2832);','} else if(t===3){ x.arc(X,Y,r,0,6.2832); } else x.arc(X,Y,r,0,6.2832);','village circle instead of mountain triangle')
one('const WIDE=(W/k)>33; const seats=((typeof SEATS!=="undefined")?SEATS:[]).filter(q=>!WIDE||(q[4]===1&&q[0]==="تهران"));','const SPAN=W/k, WIDE=SPAN>33, MS_GEO_LEVEL=WIDE?0:SPAN>15?1:SPAN>2.6?2:3; const seats=((typeof SEATS!=="undefined")?SEATS:[]).filter(q=>MS_GEO_LEVEL===0?(q[4]===1&&q[0]==="تهران"):MS_GEO_LEVEL===1?q[4]===1:MS_GEO_LEVEL===2?q[4]===1||q[4]===0:true);','map regional label policy')
one('if(kc>=GEO_T_KC[2]) for(const q of seats){ if(q[4]===2)','if(MS_GEO_LEVEL===3&&kc>=GEO_T_KC[2]) for(const q of seats){ if(q[4]===2)','county towns only')
one('const pl=GEO.ok?P.pl:[]; if(S.city&&!WIDE) for(const p of pl)', 'const pl=GEO.ok?P.pl:[]; if(S.city&&MS_GEO_LEVEL===3) for(const p of pl)','extra towns at county zoom only')
one('if(S.vill!==false && !WIDE && kc>=GEO_LV_KC[3]){ let nv=0;', 'if(S.vill!==false && MS_GEO_LEVEL===3 && kc>=GEO_LV_KC[3]){ let nv=0;','village at county zoom only')
# Preserve current reviewed OSM geo.json points and labels; add only new points (never mutate native arrays).
anchor='  x.restore(); return true;\n}\n/* =====================================================================\n   مالتی مدل سفارشی'
new='''  /* r87: additive OSM town/village/farm nodes, visible only at county-scale zoom.
     Existing SEATS/GEO locations win spatial/name dedup; no station identities are changed. */
  if((S.vill!==false||S.city!==false) && MS_GEO_LEVEL===3 && typeof window.MetStatOSM!=="undefined"){
    try{ window.MetStatOSM.drawNwp(x,W,H,k,x0,y0,scale,(P.pl||[]).concat(seats),occ,{city:S.city!==false,vill:S.vill!==false}); }catch(err){ console.warn("OSM extra places",err); }
  }
  x.restore(); return true;
}
/* =====================================================================
   مالتی مدل سفارشی'''
one(anchor,new,'inject new settlements after existing labels')
# Restrict native satellite village layer to county-scale and put additive markers on same canvas.
one('if(saLay("vill")&&(v.zl??v.z)>=7){','if(saLay("vill")&&(v.zl??v.z)>=9){','sa satellite village zoom')
one('saGeo(ctx,W,H,v,k||1); saBorders(ctx,W,H,v,k||1);','saGeo(ctx,W,H,v,k||1); if((saLay("vill")||saLay("city"))&&window.MetStatOSM){ try{window.MetStatOSM.drawSatellite(ctx,W,H,v,k||1,((typeof GEO!=="undefined"&&GEO.d&&GEO.d.places)||[]).concat(typeof SEATS!=="undefined"?SEATS:[]),{city:saLay("city"),vill:saLay("vill")})}catch(e){console.warn("OSM satellite",e)} } saBorders(ctx,W,H,v,k||1);','inject OSM in satellite canvas')
# Apply the same zoom-level hierarchy on satellite/weather layers.
one('const P=256*2**v.z, zoomAll=(v.zl??v.z)>=6.2, fs=', 'const P=256*2**v.z, spanDeg=360*W/P, fs=', 'satellite geographic scope')
one('const list=SEATS.filter(q=>q[4]===1||(zoomAll&&q[4]===0)).sort((a,b)=>(b[4]===1)-(a[4]===1)), pts=[];',
    'const list=(spanDeg>33 ? SEATS.filter(q=>q[4]===1&&q[0]==="تهران").concat((typeof GEO_CAPS!=="undefined"?GEO_CAPS:[]).map(q=>[q[0],q[1],q[2],q[3],1])) : spanDeg>15 ? SEATS.filter(q=>q[4]===1) : spanDeg>2.6 ? SEATS.filter(q=>q[4]===1||q[4]===0) : SEATS.filter(q=>q[4]<=2)).sort((a,b)=>(b[4]===1)-(a[4]===1)), pts=[];',
    'satellite capitals/provinces/counties')
# All user/meteorological logic is otherwise untouched. Script/style loaded LAST for cascade precedence.
one('</style>\n</body>\n</html>', '</style>\n<script src="assets/metstat_osm_settlements_v87.js?v=87"></script>\n<link rel="stylesheet" href="assets/metstat_desktop_shell_v87.css?v=87">\n</body>\n</html>', 'add external OSM renderer and desktop shell')
assert s.count('metstat_desktop_shell_v87.css')==1
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(s,encoding='utf-8')
print('Patched',base,'->',out,hashlib.sha256(s.encode()).hexdigest())
