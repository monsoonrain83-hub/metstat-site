"""Build a narrow manifest revalidation update from an exact V81 baseline."""
from pathlib import Path
import hashlib
import sys
import urllib.request

CORE = 'ms_r5_perf_core_482de779e30b7f58.js'
INDEX_SHA = '219efe2c2d5eac09bffbe03fa8490920769d8dd0ccb90fa7ff6f739039881eb2'
CORE_SHA = '482de779e30b7f58b2cae35bf2f3e1851b1603bfdddab8868c4fd1341d20f01f'
OLD = 'let r=null; for(let k=0;k<3&&!(r&&r.ok);k++){ const ac=new AbortController(), tm=setTimeout(()=>ac.abort(),k?20000:12000); try{ r=await fetch(ON.base+"data/manifest.json?"+Date.now(),{cache:"no-store",signal:ac.signal}); }catch(_){ r=null; } clearTimeout(tm); } if(!r||!r.ok) throw new Error(r?r.status:"timeout"); ON.man=await r.json();'
HELPER = '''async function ms82FetchManifest(base){
  // Stable public URL: revalidate on every load. No stale-while-revalidate or TTL.
  // Preserve the original cache-bypassing URL as the fallback for errors.
  let last;
  for(let k=0;k<3;k++){
    const ac=new AbortController(),tm=setTimeout(()=>ac.abort(),k?20000:12000);
    try{
      const path=base+"data/manifest.json"+(k?"?"+Date.now():"");
      const r=await fetch(path,{cache:k?"no-store":"no-cache",signal:ac.signal});
      if(!r.ok)throw new Error("manifest HTTP "+r.status);
      const m=await r.json();
      if(!m||typeof m!=="object"||!m.models||typeof m.models!=="object"||!Array.isArray(m.items)||(m.items_prev!==undefined&&!Array.isArray(m.items_prev)))throw new Error("invalid manifest schema");
      return m;
    }catch(e){last=e;}finally{clearTimeout(tm);}
  }
  throw last||new Error("manifest unavailable");
}
'''

def digest(b): return hashlib.sha256(b).hexdigest()

def replace_once(s,a,b):
    if s.count(a)!=1: raise ValueError('baseline anchor mismatch')
    return s.replace(a,b,1)

def build(index,core):
    if digest(index)!=INDEX_SHA or digest(core)!=CORE_SHA: raise ValueError('V81 baseline mismatch')
    s=index.decode('utf-8');c=core.decode('utf-8')
    c=replace_once(c,OLD,'ON.man=await ms82FetchManifest(ON.base);')
    c=replace_once(c,'async function onLoadManifest(){',HELPER+'async function onLoadManifest(){')
    b=c.encode('utf-8');name='ms_r5_perf_core_'+digest(b)[:16]+'.js'
    s=replace_once(s,'<script src="/assets/'+CORE+'"></script>','<script src="/assets/'+name+'"></script>')
    return s.encode('utf-8'),b,name

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw): return None

def read_live(path,limit):
    req=urllib.request.Request('https://wtafkik.ir'+path,headers={'Accept-Encoding':'identity','Cache-Control':'no-cache','User-Agent':'MetStat-V82-verification/1.0'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=45) as r:
        b=r.read(limit+1)
        if r.status!=200 or len(b)>limit: raise ValueError('invalid public response')
        return b

if __name__=='__main__':
    if len(sys.argv)==2:
        root=Path(sys.argv[1]);index=(root/'index.html').read_bytes();core=(root/'assets'/CORE).read_bytes()
    else:
        index=read_live('/',2_000_000);core=read_live('/assets/'+CORE,6_000_000)
    index,core,name=build(index,core)
    dest=Path('v82-candidate');(dest/'assets').mkdir(parents=True,exist_ok=True)
    (dest/'index.html').write_bytes(index);(dest/'assets'/name).write_bytes(core)
    print('candidate:',digest(index),name,digest(core))
