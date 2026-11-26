"""Narrow index optimization for exact V82 production frontend."""
from pathlib import Path
import hashlib, urllib.request
CORE='ms_r5_perf_core_eca95cc1c84b0ff5.js'
INDEX_SHA='adf50bd8e9a2f0402d9b33acfb44cda8dfd236ae22d268c9adf94f8fc306e362'
CORE_SHA='eca95cc1c84b0ff52374230abb0c03cf2802e10fe706173dd872746b6c7cd1e0'
OLD='function nvMeItems(m){ return (m?nvItemsSrc(m):(ON.man?ON.man.items:[])).filter(i=>i.r==="me" && (!m||i.m===m) && !/L$/.test(i.p)); }'
NEW='''// V85: index each manifest array once. Arrays are replaced on manifest load/prune.
const NV_ME_INDEX=new WeakMap();
function nvMeItems(m){
  const man=ON.man;
  if(!man) return [];
  const src=m&&nvRunIsPrev(m)?(man.items_prev||[]):(man.items||[]);
  let idx=NV_ME_INDEX.get(src);
  if(!idx||idx.length!==src.length){
    const all=[],byModel=new Map();
    for(const i of src){
      if(i.r!=="me"||/L$/.test(i.p))continue;
      all.push(i);
      let rows=byModel.get(i.m);
      if(!rows){rows=[];byModel.set(i.m,rows);}
      rows.push(i);
    }
    idx={length:src.length,all,byModel};NV_ME_INDEX.set(src,idx);
  }
  // Preserve legacy fresh-array semantics and original row identity/order.
  return (m?(idx.byModel.get(m)||[]):idx.all).slice();
}'''
def patch_menu(s):
    replacements=[
      ('function nvBarRefresh(){ const bar=$("nvBar"); if(bar&&ON.man) bar.innerHTML=wxModelChips(); }', '''const NV_BAR_BOUND=new WeakSet(), NV_BAR_RENDERED=new WeakMap();
function nvBindModelBar(bar){
  if(!bar||NV_BAR_BOUND.has(bar))return;
  bar.addEventListener("click",e=>{ const b=e.target.closest("button[data-m]"); if(!b||b.disabled||!bar.contains(b))return; NV.s.m=b.dataset.m; $("nvM").value=NV.s.m; nvFillRun(); });
  NV_BAR_BOUND.add(bar);
}
function nvBarRefresh(){
  const bar=$("nvBar"); if(!bar||!ON.man)return;
  nvBindModelBar(bar);
  const html=wxModelChips(), prev=NV_BAR_RENDERED.get(bar);
  if(prev&&prev.html===html&&prev.serialized===bar.innerHTML)return;
  bar.innerHTML=html;
  NV_BAR_RENDERED.set(bar,{html,serialized:bar.innerHTML});
}'''),
      ('const bar=$("nvBar"); if(bar) bar.innerHTML=wxModelChips(); try{ const rb=', 'nvBarRefresh(); try{ const rb='),
      ('  if(bar) bar.addEventListener("click",e=>{ const b=e.target.closest("button[data-m]"); if(b) pickModel(b.dataset.m); });','  nvBindModelBar(bar);')]
    for old,new in replacements:
        if s.count(old)!=1: raise ValueError('menu patch anchor mismatch: '+old[:100])
        s=s.replace(old,new,1)
    return s
def sha(b): return hashlib.sha256(b).hexdigest()
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
def fetch(path,limit,expected=None):
    req=urllib.request.Request('https://wtafkik.ir'+path,headers={'Accept-Encoding':'identity','Cache-Control':'no-cache'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=45) as r:
        b=r.read(limit+1)
        if r.status!=200 or len(b)>limit or (expected and sha(b)!=expected): raise ValueError('live baseline mismatch: '+path)
        return b
def build(index,core):
    if sha(index)!=INDEX_SHA or sha(core)!=CORE_SHA:raise ValueError('V82 baseline mismatch')
    s=index.decode();c=core.decode()
    if c.count(OLD)!=1:raise ValueError('patch anchor mismatch')
    c=patch_menu(c.replace(OLD,NEW,1));b=c.encode();name='ms_r5_perf_core_'+sha(b)[:16]+'.js'
    ref='<script src="/assets/'+CORE+'"></script>'
    if s.count(ref)!=1:raise ValueError('core ref mismatch')
    return s.replace(ref,'<script src="/assets/'+name+'"></script>',1).encode(),b,name
if __name__=='__main__':
    index=fetch('/',2_000_000,INDEX_SHA);core=fetch('/assets/'+CORE,6_000_000,CORE_SHA)
    root=Path('v85-baseline');(root/'assets').mkdir(parents=True,exist_ok=True)
    (root/'index.html').write_bytes(index);(root/'assets'/CORE).write_bytes(core)
    index,c,n=build(index,core);out=Path('v85-candidate');(out/'assets').mkdir(parents=True,exist_ok=True)
    (out/'index.html').write_bytes(index);(out/'assets'/n).write_bytes(c)
    Path('v85-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    print(sha(index),n,sha(c))
