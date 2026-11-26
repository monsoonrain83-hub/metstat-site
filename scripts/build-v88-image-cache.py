"""Replace the V87 count-only cache with a single canonical byte-bounded owner."""
from pathlib import Path
import hashlib, urllib.request
CORE='ms_r5_perf_core_4a4e77930c1b17d3.js'
INDEX_SHA='0adaeabb312653692ba463a0bc6c0d24e19a79d9c125ed53aed59eea809ed785'
CORE_SHA='4a4e77930c1b17d3fc39353d32d3c88ac9691edb69d108f84718c1ae49eb239e'
def sha(b): return hashlib.sha256(b).hexdigest()
def build(index,core,module):
    if sha(index)!=INDEX_SHA or sha(core)!=CORE_SHA: raise ValueError('V87 baseline mismatch')
    c=core.decode('utf8');anchor='view:null, entry:null, tok:0, cache:new Map(), paths:null'
    if c.count(anchor)!=1 or c.count('function nvImg(url){')!=1 or c.count('NV.cache')!=8: raise ValueError('cache ownership mismatch')
    c=c.replace(anchor,'view:null, entry:null, tok:0, paths:null',1)
    a=c.index('function nvImg(url){');b=c.index('async function nvResolve(){',a)
    marker='export function createForecastImageCache('
    if module.count(marker)!=1: raise ValueError('module export mismatch')
    module=module.replace(marker,'function createForecastImageCache(',1)
    bridge='''
const NV_IMAGE_CACHE=createForecastImageCache(url=>new Promise(res=>{const im=new Image();im.onload=()=>res(im);im.onerror=()=>res(null);im.src=url;}));
function nvImg(url){ return NV_IMAGE_CACHE.get(url); }
'''
    c=c[:a]+module+bridge+c[b:]
    if 'NV.cache' in c or c.count('function createForecastImageCache(')!=1: raise ValueError('duplicate cache owner')
    out=c.encode('utf8');name='ms_r5_perf_core_'+sha(out)[:16]+'.js';ref=('<script src="/assets/'+CORE+'"></script>').encode()
    if index.count(ref)!=1: raise ValueError('core reference mismatch')
    return index.replace(ref,('<script src="/assets/'+name+'"></script>').encode(),1),out,name
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw):return None
def fetch(path,limit,expected=None):
    req=urllib.request.Request('https://wtafkik.ir'+path,headers={'Accept-Encoding':'identity','Cache-Control':'no-cache'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=45) as r:
        data=r.read(limit+1)
        if r.status!=200 or len(data)>limit or (expected and sha(data)!=expected):raise ValueError('live baseline mismatch: '+path)
        return data
if __name__=='__main__':
    i,c=fetch('/',2_000_000,INDEX_SHA),fetch('/assets/'+CORE,6_000_000,CORE_SHA)
    base=Path('v88-baseline');(base/'assets').mkdir(parents=True,exist_ok=True);(base/'index.html').write_bytes(i);(base/'assets'/CORE).write_bytes(c)
    Path('v88-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    i,c,n=build(i,c,(Path(__file__).resolve().parents[1]/'web/forecast/image-cache.mjs').read_text(encoding='utf8'))
    out=Path('v88-candidate');(out/'assets').mkdir(parents=True,exist_ok=True);(out/'index.html').write_bytes(i);(out/'assets'/n).write_bytes(c)
    print(sha(i),n,sha(c))
