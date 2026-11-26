"""V86: small optimizations applied only to the SHA-pinned live V85 baseline."""
from pathlib import Path
import hashlib, urllib.request
from importlib.machinery import SourceFileLoader
chip=SourceFileLoader('chips',str(Path(__file__).with_name('optimize-model-chips.py'))).load_module()
CORE='ms_r5_perf_core_cf0e22054ebb398d.js'
INDEX_SHA='a2ccae8db2de9b070fb30c8fcf4702fc12751e29a2f6fbd1fef5cb2c878950d2'
CORE_SHA='cf0e22054ebb398d39d5ff12501a2f1cb2b7229e907c3bdc02121966b2a1ac05'
OLD='function nvEuItems(m,pid){ return (nvItemsSrc(m)||[]).filter(i=>i.r==="eu"&&i.m===m&&i.p===pid&&!/[LHVW]$/.test(i.p)); }'
NEW='''// V86: independent index for European tiles; same selected run and row order.
const NV_EU_INDEX=new WeakMap();
function nvEuItems(m,pid){
  const man=ON.man;
  if(!man) return [];
  const src=nvRunIsPrev(m)?(man.items_prev||[]):(man.items||[]);
  let idx=NV_EU_INDEX.get(src);
  if(!idx||idx.length!==src.length){
    const byModel=new Map();
    for(const i of src){
      if(i.r!=="eu"||/[LHVW]$/.test(i.p)) continue;
      let params=byModel.get(i.m);
      if(!params){params=new Map();byModel.set(i.m,params);}
      let rows=params.get(i.p);
      if(!rows){rows=[];params.set(i.p,rows);}
      rows.push(i);
    }
    idx={length:src.length,byModel};NV_EU_INDEX.set(src,idx);
  }
  return (idx.byModel.get(m)?.get(pid)||[]).slice();
}'''
def sha(b):return hashlib.sha256(b).hexdigest()
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw):return None
def fetch(path,limit,expected=None):
    req=urllib.request.Request('https://wtafkik.ir'+path,headers={'Accept-Encoding':'identity','Cache-Control':'no-cache'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=45) as r:
        data=r.read(limit+1)
        if r.status!=200 or len(data)>limit or (expected and sha(data)!=expected):raise ValueError('live baseline mismatch: '+path)
        return data
def build(index,core):
    if sha(index)!=INDEX_SHA or sha(core)!=CORE_SHA:raise ValueError('V85 baseline mismatch')
    c=chip.patch(core.decode('utf8'))
    if c.count(OLD)!=1:raise ValueError('EU anchor mismatch')
    c=c.replace(OLD,NEW,1).encode('utf8')
    name='ms_r5_perf_core_'+sha(c)[:16]+'.js'
    ref=('<script src="/assets/'+CORE+'"></script>').encode()
    if index.count(ref)!=1:raise ValueError('core ref mismatch')
    return index.replace(ref,('<script src="/assets/'+name+'"></script>').encode(),1),c,name
if __name__=='__main__':
    i,c=fetch('/',2_000_000,INDEX_SHA),fetch('/assets/'+CORE,6_000_000,CORE_SHA)
    base=Path('v86-baseline');(base/'assets').mkdir(parents=True,exist_ok=True)
    (base/'index.html').write_bytes(i);(base/'assets'/CORE).write_bytes(c)
    i,c,name=build(i,c)
    root=Path('v86-candidate');(root/'assets').mkdir(parents=True,exist_ok=True)
    (root/'index.html').write_bytes(i);(root/'assets'/name).write_bytes(c)
    Path('v86-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    print(sha(i),name,sha(c))
