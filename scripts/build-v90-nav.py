"""V90: replace redundant writes in two existing navigation sync owners.
No new persistent observer, interval, route, or scientific calculation.
Build only from the SHA-pinned V89 artifact.
"""
from pathlib import Path
import hashlib, json, zipfile, runpy
from verify_frontend_release import inspect_zip

sha=lambda b:hashlib.sha256(b).hexdigest()
BASE_ZIP='6cc8547b491cf81734d47584f0c9eb230cf8242e7bb5dac13c660c92c1bc8834'
BASE_INDEX='a27298eb66145a9a8890d21c57330058876b2dd75b0b81604242b62ff9151936'
BASE_CORE='cc3b5fc40594635e03338489bd03fb205de19573938926988d1924f869f92631'
NEXT_INDEX='22368db76d7c67f4534f8abdf9de5f54eee1160777c56548bba1872c8de58a2c'
NEXT_CORE='ee373baac9806769233f4c15a7c72887026e8b766a34f86a5e3af694be31f7a3'
CHANGES=[
('const isLand=!land.hidden; nav.hidden=isLand; adr.hidden=isLand;', 'const isLand=!land.hidden; if(nav.hidden!==isLand) nav.hidden=isLand; if(adr.hidden!==isLand) adr.hidden=isLand;'),
('document.title = isLand||!name ? TITLE0 : name+" — MetStat";\n    adr.querySelector(".pa-u").textContent=location.host+location.pathname+location.hash;', 'const title=isLand||!name ? TITLE0 : name+" — MetStat"; if(document.title!==title) document.title=title;\n    const addr=adr.querySelector(".pa-u"), url=location.host+location.pathname+location.hash; if(addr.textContent!==url) addr.textContent=url;'),
('const mo=new MutationObserver(()=>setTimeout(sync,60));\n  for(const id of ["landing","app","dsApp","cvApp","ltApp","wnApp","cqcApp","caApp","onApp","ciApp","saApp","anApp"])', 'let syncTimer=null; const scheduleSync=delay=>{ if(syncTimer!==null) return; syncTimer=setTimeout(()=>{ syncTimer=null; sync(); },delay); };\n  const mo=new MutationObserver(()=>scheduleSync(60));\n  for(const id of ["landing","app","dsApp","cvApp","ltApp","wnApp","cqcApp","caApp","onApp","ciApp","saApp","anApp"])'),
('addEventListener("popstate",()=>setTimeout(sync,80)); addEventListener("hashchange",()=>setTimeout(sync,80));\n  setInterval(sync,1500); sync();', 'addEventListener("popstate",()=>scheduleSync(80)); addEventListener("hashchange",()=>scheduleSync(80));\n  setInterval(sync,1500); sync();'),
('hubM.hidden=!(vis&&MAIN.includes(k)); hubO.hidden=!(vis&&OFF.includes(k));', 'const mainHidden=!(vis&&MAIN.includes(k)), offHidden=!(vis&&OFF.includes(k));\n    if(hubM.hidden!==mainHidden) hubM.hidden=mainHidden; if(hubO.hidden!==offHidden) hubO.hidden=offHidden;'),
('hb.title=lab; hb.setAttribute("aria-label",lab);', 'if(hb.title!==lab) hb.title=lab; if(hb.getAttribute("aria-label")!==lab) hb.setAttribute("aria-label",lab);'),
('const mo=new MutationObserver(()=>setTimeout(sync,40));\n  for(const id of ["landing","app","dsApp","cvApp","ltApp","wnApp","cqcApp","caApp","onApp","ciApp","saApp","anApp","labApp","synApp","drApp","mtApp"])', 'let syncTimer=null; const scheduleSync=delay=>{ if(syncTimer!==null) return; syncTimer=setTimeout(()=>{ syncTimer=null; sync(); },delay); };\n  const mo=new MutationObserver(()=>scheduleSync(40));\n  for(const id of ["landing","app","dsApp","cvApp","ltApp","wnApp","cqcApp","caApp","onApp","ciApp","saApp","anApp","labApp","synApp","drApp","mtApp"])'),
('addEventListener("popstate",()=>setTimeout(sync,80)); addEventListener("hashchange",()=>setTimeout(sync,80));\n  document.addEventListener("langchange",()=>{ hubTxt(); if(!dr.hidden) drFill(); });','addEventListener("popstate",()=>scheduleSync(80)); addEventListener("hashchange",()=>scheduleSync(80));\n  document.addEventListener("langchange",()=>{ hubTxt(); if(!dr.hidden) drFill(); });')]
def build(index,core):
    if sha(index)!=BASE_INDEX or sha(core)!=BASE_CORE: raise ValueError('unexpected V89 pair')
    s=core.decode('utf-8')
    for a,b in CHANGES:
        if s.count(a)!=1:raise ValueError('navigation ownership mismatch')
        s=s.replace(a,b,1)
    out=s.encode('utf-8')
    for key in ('setInterval(','new MutationObserver('):
        if core.count(key.encode())!=out.count(key.encode()):raise ValueError('unexpected new timer/observer')
    old=('assets/ms_r5_perf_core_'+BASE_CORE[:16]+'.js').encode()
    name='assets/ms_r5_perf_core_'+NEXT_CORE[:16]+'.js'
    if index.count(old)!=1:raise ValueError('unexpected HTML reference')
    html=index.replace(old,name.encode(),1)
    if sha(out)!=NEXT_CORE or sha(html)!=NEXT_INDEX:raise ValueError('local/CI candidate mismatch')
    return html,out,name
def write_pair(root,index,core,name):
    p=Path(root);(p/'assets').mkdir(parents=True,exist_ok=True)
    (p/'index.html').write_bytes(index);(p/name).write_bytes(core)
if __name__=='__main__':
    z=Path('v89-artifact/MetStat_V89_upload.zip')
    if sha(z.read_bytes())!=BASE_ZIP:raise ValueError('unexpected V89 artifact')
    i,c,n,_=inspect_zip(z)
    if n!='assets/ms_r5_perf_core_'+BASE_CORE[:16]+'.js':raise ValueError('unexpected core filename')
    write_pair('v90-baseline',i,c,n)
    html,core,name=build(i,c)
    write_pair('v90-candidate',html,core,name)
    fetch=runpy.run_path(str(Path(__file__).with_name('build-v89-tile-raster.py')))['fetch']
    approved={'0adaeabb312653692ba463a0bc6c0d24e19a79d9c125ed53aed59eea809ed785':'4a4e77930c1b17d3fc39353d32d3c88ac9691edb69d108f84718c1ae49eb239e','52012e1fd5ff0921dbc49823b311b062752dfd3ac17dbbe46503e438587836e6':'e8ff91ddd6acd9597556fb17c60e4ffec6d816c3302bfdd3bde2faf455dda040',BASE_INDEX:BASE_CORE}
    h=sha(fetch('/',2_000_000))
    if h not in approved:raise ValueError('unrecognized live HTML')
    d=approved[h]
    if sha(fetch('/assets/ms_r5_perf_core_'+d[:16]+'.js',6_000_000))!=d:raise ValueError('live HTML/core mismatch')
    Path('v90-live-baseline.json').write_text(json.dumps({'index_sha256':h,'core_sha256':d}))
    Path('v90-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    print(sha(html),name,sha(core))
