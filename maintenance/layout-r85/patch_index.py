from pathlib import Path
import hashlib,re,argparse
ap=argparse.ArgumentParser(description='MetStat r85 safe, source-hash-checked HTML patch')
ap.add_argument('--input',default='index.html',help='Current live-base index.html')
ap.add_argument('--output',default='index_r85.html',help='Patched candidate, never overwrites input')
args=ap.parse_args()
source=Path(args.input).resolve()
s=source.read_text(encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='b5005c16ebaba3994d98f7ffe151115e38e46e5ce0d775c7ece08b140397bd80'
changes=[]
def one(old,new,label):
 global s
 c=s.count(old)
 if c!=1:raise ValueError((label,c))
 s=s.replace(old,new,1);changes.append(label)
# Do not force an inaccessible fixed pixel viewport on phones (still retain existing desktop layouts at real desktop breakpoints).
one("var desktop='width=1220, initial-scale=1, user-scalable=yes', full='width=device-width, initial-scale=1, user-scalable=yes';",
    "var desktop='width=device-width, initial-scale=1, user-scalable=yes', full='width=device-width, initial-scale=1, user-scalable=yes';",
    'Viewport: respect physical device width')
# Duplicate event forwarding after relocated mirrors: the existing document change delegate at nvrBuild already forwards.
one("document.addEventListener('change',function(ev){var e=ev.target;if(!e||!e.closest||!e.closest('#onAside #nvR7')||!e.dataset||!e.dataset.mir)return;var original=document.getElementById(e.dataset.mir);if(original&&original!==e){original.value=e.value;original.dispatchEvent(new Event('change',{bubbles:true}));}},true);",
    "/* r85: canonical mirror change dispatch is already handled by nvrBuild's document listener.\n   Avoid a second change event for relocated sidebar selectors. */",
    'Remove duplicate mirrored select event dispatch')
# Old r160 move-back timer fights with the P8 600ms move-to-aside interval.
old='''/* r160: روی دسکتاپ، منوی «تاریخ و ساعت پیش‌بینی» در ستون کناری صفحه می‌نشیند؛ روی موبایل زیر نقشه */
setInterval(()=>{ try{ const nm=document.getElementById("nvMenus"), as=document.getElementById("onAside"); if(!nm||!as) return; const wide=window.innerWidth>=1000&&!document.body.classList.contains("nvfOn");
  if(wide&&nm.parentNode!==as){ if(!nm.__home) nm.__home={p:nm.parentNode,n:nm.nextSibling}; as.prepend(nm); }
  else if(!wide&&nm.__home&&nm.parentNode===as){ const h=nm.__home; (h.n&&h.n.parentNode===h.p)?h.p.insertBefore(nm,h.n):h.p.append(nm); } }catch(e){} },700);'''
one(old,'/* r85: r160 700ms menu mover removed. The P8 relocation controller owns both move and restore. */','Remove competing menu mover')
# Toggle event handler should work on controls after moving outside card.
old='''  card.addEventListener("toggle",e=>{ const d=e.target; if(!d||!d.matches||!d.matches(".nvR6 details,.nvR7 details")||!d.open) return;
    card.querySelectorAll(".nvR6 details[open],.nvR7 details[open]").forEach(o=>{ if(o!==d) o.open=false; });
    const sm=d.querySelector("summary"), p=d.querySelector(".ovp"); if(!sm||!p) return;
    const r=sm.getBoundingClientRect(), vh=window.innerHeight; let top=r.bottom+4, mh=vh-top-8;
    if(mh<180){ top=Math.max(8,r.top-4-Math.min(360,vh*.6)); mh=Math.min(360,vh*.6); }
    p.style.top=top+"px"; p.style.maxHeight=Math.max(140,mh)+"px"; },true);
  document.addEventListener("click",e=>{ if(e.target.closest(".nvR6 details,.nvR7 details")) return; card.querySelectorAll(".nvR6 details[open],.nvR7 details[open]").forEach(o=>o.open=false); });'''
new='''  /* r85: delegate on document so menus relocated into #onAside still receive toggle events. */
  if(!document.__msNvMenuHandlers){
    document.__msNvMenuHandlers=true;
    const ddSel="#onApp .nvR6 details,#onApp .nvR7 details,#onAside .ovd";
    document.addEventListener("toggle",e=>{ const d=e.target; if(!d||!d.matches||!d.matches(ddSel)||!d.open) return;
      document.querySelectorAll("#onApp .nvR6 details[open],#onApp .nvR7 details[open],#onAside .ovd[open]").forEach(o=>{if(o!==d)o.open=false;});
      const sm=d.querySelector("summary"),panel=d.querySelector(".ovp");if(!sm||!panel)return;
      if(d.closest("#onAside")){panel.style.removeProperty("top");panel.style.removeProperty("max-height");return;}
      const r=sm.getBoundingClientRect(),vh=window.innerHeight;let top=r.bottom+4,mh=vh-top-8;
      if(mh<180){top=Math.max(8,r.top-4-Math.min(360,vh*.6));mh=Math.min(360,vh*.6);}
      panel.style.top=top+"px";panel.style.maxHeight=Math.max(140,mh)+"px";
    },true);
    document.addEventListener("click",e=>{if(e.target.closest(ddSel))return;
      document.querySelectorAll("#onApp .nvR6 details[open],#onApp .nvR7 details[open],#onAside .ovd[open]").forEach(d=>d.open=false);
    });
  }'''
one(old,new,'Delegate dropdown toggles for relocated menus and close outside reliably')
# One relocation routine with consistent move/restore: no race and preserve node original event handlers.
old='''function relocate(){if(isFs()||busy)return;var side=document.getElementById('onAside'),card=document.querySelector('#onViewer .nvCard[data-rows]');if(!side||!card||!card.isConnected)return;
 busy=true;try{
 var r=document.getElementById('nvR7');if(r&&r.parentElement!==side)side.insertBefore(r,side.firstChild);
 var t=toolsFor(side);
 ['.nvCbDd','.nvRegBar','#nvBm','.nvLayDd','.nvHlDd','.nvOvlDd','#nvWindBox','.nvBrdDd','.nvWindDd'].forEach(function(sel){var e=card.querySelector(sel)||t.querySelector(sel);if(!e)return;if(e.id==='nvBm'&&e.closest('label'))e=e.closest('label');if(e.parentElement!==t)t.appendChild(e);});
 var nm=document.getElementById('nvMenus');if(nm&&nm.parentElement!==side)side.appendChild(nm);
 }finally{busy=false;}}'''
new='''function remember(e){if(e&&!e.__msHome)e.__msHome={p:e.parentNode,n:e.nextSibling};}
function restore(e){var h=e&&e.__msHome;if(!h||!h.p||!h.p.isConnected||e.parentNode===h.p)return;
  if(h.n&&h.n.parentNode===h.p)h.p.insertBefore(e,h.n);else h.p.appendChild(e);}
function relocate(){if(isFs()||busy)return;var side=document.getElementById('onAside'),card=document.querySelector('#onViewer .nvCard[data-rows]');if(!side||!card||!card.isConnected)return;
 busy=true;try{
  var r=document.getElementById('nvR7'),nm=document.getElementById('nvMenus'),t=document.getElementById('p8Tools');
  if(window.innerWidth<1000){restore(r);restore(nm);if(t){Array.from(t.children).forEach(restore);}return;}
  if(r&&r.parentElement!==side){remember(r);side.insertBefore(r,side.firstChild);}
  t=toolsFor(side);
  ['.nvCbDd','.nvRegBar','#nvBm','.nvLayDd','.nvHlDd','.nvOvlDd','#nvWindBox','.nvBrdDd','.nvWindDd'].forEach(function(sel){var e=card.querySelector(sel)||t.querySelector(sel);if(!e)return;if(e.id==='nvBm'&&e.closest('label'))e=e.closest('label');if(e.parentElement!==t){remember(e);t.appendChild(e);}});
  if(nm&&nm.parentElement!==side){remember(nm);side.appendChild(nm);}
 }finally{busy=false;}}'''
one(old,new,'Single relocation controller with restoration on narrow viewports')
# Fix CSS with a new last override that does not modify old layout for wide desktop.
css='''<style id="metstat-r85-navigation-dropdown-layout">
/* r85: The old P8/P15 1220px min-width and fixed viewport hid controls on actual narrow screens. */
@media (max-width:1199px){
 html:not(.nvfOn),html:not(.nvfOn) body{min-width:0!important;width:100%!important;max-width:100%!important}
 html:not(.nvfOn) body .wrap{max-width:100%!important;min-width:0!important}
 :is(#drApp,#mtApp,#apApp,#flApp,#obApp,#sfApp,#ciApp,#saApp,#anApp,#labApp,#synApp):not([hidden]){min-width:0!important;max-width:100%!important;width:100%!important}
 .top,.top-in,#msNav,#menuBar{min-width:0!important;max-width:100%!important;box-sizing:border-box!important}
 .top-in{flex-wrap:wrap!important;gap:8px!important;padding:8px!important}
 .top-in .ttl{min-width:0!important;flex:1 1 250px!important}
 .top-in .ttl h1{overflow-wrap:anywhere}
 .top-in .hdr-r{min-width:0!important;max-width:100%!important;flex:0 1 auto!important;flex-wrap:wrap!important}
 #menuBar{padding-inline:8px!important;flex-wrap:wrap!important}
 #onApp:not([hidden]){min-width:0!important;max-width:100%!important;width:100%!important}
}
/* All global navigation buttons remain readable and reachable by horizontal scrolling. */
#msNavR1,#msNavR2{overflow-x:auto!important;overflow-y:hidden!important;overscroll-behavior-x:contain;scrollbar-width:thin;-webkit-overflow-scrolling:touch}
#msNavR1>*,#msNavR2>*{flex:0 0 auto!important;min-width:max-content!important;max-width:none!important;max-height:none!important;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important}
/* Drop-down content inside a scrollable sidebar must be in normal flow or it is clipped.
   overflow-y:auto + overflow-x:visible computes to auto/auto by CSS rules. */
#onAside #p8Tools .ovd[open]>.ovp,#onAside #nvMenus .ovd[open]>.ovp,
#onAside .ovd[open]>.ovp{position:static!important;inset:auto!important;top:auto!important;right:auto!important;left:auto!important;bottom:auto!important;transform:none!important;min-width:0!important;width:100%!important;max-width:100%!important;max-height:45vh!important;overflow-y:auto!important;overflow-x:hidden!important;box-sizing:border-box!important;margin-top:5px!important;z-index:auto!important}
#onAside #p8Tools .ovd,#onAside #nvMenus .ovd{min-width:0!important;width:100%!important;max-width:100%!important}
#onAside :is(summary,button,select,input){box-sizing:border-box;max-width:100%}
#onAside .ovd>summary{white-space:normal!important;overflow-wrap:anywhere}
/* A relocatable dropdown must be present in the card on small widths. */
@media (max-width:999px){
 #onApp:not([hidden]){display:flex!important;flex-direction:column!important;gap:10px!important;align-items:stretch!important}
 #onViewer,#onAside{position:static!important;grid-column:auto!important;grid-row:auto!important;min-width:0!important;width:100%!important;max-width:100%!important;max-height:none!important;overflow:visible!important}
 #onViewer .nvR7{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:5px!important}
 #onViewer .nvR7 select{min-width:0!important;max-width:100%!important;box-sizing:border-box!important}
 #onViewer .nvR6{max-width:100%!important;min-width:0!important;flex-wrap:wrap!important}
 #onViewer .nvR6 .ovd{min-width:0!important}
 #onViewer .nvR6 .ovp{position:static!important;inset:auto!important;min-width:0!important;width:100%!important;max-width:100%!important;max-height:45vh!important;overflow:auto!important;box-sizing:border-box!important}
}
/* Avoid controls or floating suggestions crossing the viewport edge. */
.drFly{max-width:min(300px,calc(100vw - 16px))!important;max-height:min(75vh,700px)!important;overflow-y:auto!important;box-sizing:border-box!important}
#menuBar [role="menu"],#menuBar .dropdown-menu,#menuBar .userMenu{max-width:min(310px,calc(100vw - 16px))!important;box-sizing:border-box!important}
</style>'''
assert s.rstrip().endswith('</html>')
idx=s.rfind('</body>')
assert idx>0
s=s[:idx]+css+'\n'+s[idx:]
changes.append('Append last-scoped responsive and dropdown CSS')
# Avoid registering a new global mirror event listener whenever the map card is rebuilt.
old="""  document.addEventListener("change",e=>{ const t=e.target; if(!t||!t.id||!t.closest("#nvR7")) return;
    if(t.dataset.mir){ wxSet(t.dataset.mir,t.value); }
    else if(t.id==="nvX4"){ NVR.pt=t.value; const c=[...$("nvCat").options].find(o=>!o.disabled&&((o.value==="sc")===(t.value==="s"))); if(c) wxSet("nvCat",c.value); else nvrSync(true); }
    else if(t.id==="nvX5") wxSet("nvCat",t.value); });"""
new="""  if(!document.__msNvMirrorDelegate){document.__msNvMirrorDelegate=true;
    document.addEventListener("change",e=>{ const t=e.target; if(!t||!t.id||!t.closest("#nvR7")) return;
      if(t.dataset.mir){ wxSet(t.dataset.mir,t.value); }
      else if(t.id==="nvX4"){ NVR.pt=t.value; const c=[...$("nvCat").options].find(o=>!o.disabled&&((o.value==="sc")===(t.value==="s"))); if(c) wxSet("nvCat",c.value); else nvrSync(true); }
      else if(t.id==="nvX5") wxSet("nvCat",t.value); });
  }"""
one(old,new,'Register global mirrored-select listener only once')
# Make unlabeled controls accessible to screen readers.
one('<select id="tplPreset" class="btn sm">','<select id="tplPreset" class="btn sm" aria-label="انتخاب مقیاس رنگ آماده">','Add accessible label to colorbar selector')
one('<input id="region" value="ایران" placeholder="نام منطقه را بنویسید" hidden>','<input id="region" value="ایران" placeholder="نام منطقه را بنویسید" aria-label="نام منطقه" hidden>','Add accessible label to region fallback')
# The late guard CSS was chosen rather than rebuilding all existing styles or removing the desktop map layouts.
out=Path(args.output).resolve()
if out==source:raise ValueError('Refusing to overwrite the input index.html')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(s,encoding='utf-8')
print({'changes':changes,'size':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
