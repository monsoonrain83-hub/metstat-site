"""Build from the exact previously browser-verified V88 artifact, never from a historical host snapshot."""
from pathlib import Path
import hashlib, zipfile, urllib.request, json
from verify_frontend_release import inspect_zip
CORE='ms_r5_perf_core_e8ff91ddd6acd959.js'
INDEX_SHA='52012e1fd5ff0921dbc49823b311b062752dfd3ac17dbbe46503e438587836e6'
CORE_SHA='e8ff91ddd6acd9597556fb17c60e4ffec6d816c3302bfdd3bde2faf455dda040'
ZIP_SHA='1daee3717fc67d657870a949c441a964e4ce437a432c2d1fb5886283bb8da5df'
def sha(b): return hashlib.sha256(b).hexdigest()
def build(index, core, module):
    if sha(index)!=INDEX_SHA or sha(core)!=CORE_SHA: raise ValueError('V88 baseline mismatch')
    c=core.decode('utf8')
    a=c.index('      for(let py=0;py<h;py++){ const v=(ay+py+0.5-dy)/f-0.5',c.index('function nvPaintTile('))
    b=c.index('      x.putImageData(out,ax,ay);',a)
    if c[a:b].count('o32[py*w+px]')!=1: raise ValueError('raster loop mismatch')
    c=c[:a]+'      rasterForecastTile(o32,w,h,ax,ay,dx,dy,f,I,W0,H0,pal);\n'+c[b:]
    old='const out=new ImageData(w,h), o32=new Uint32Array(out.data.buffer), pal=nvPal32(nvEffScale(e)), n=pal.length, W0=NV_TW, H0=NV_TH, WHITE=0xFFFFFFFF;'
    if c.count(old)!=1 or c.count('function nvPaintTile(')!=1 or 'function rasterForecastTile(' in c: raise ValueError('raster ownership mismatch')
    c=c.replace(old,'const out=new ImageData(w,h), o32=new Uint32Array(out.data.buffer), pal=nvPal32(nvEffScale(e)), W0=NV_TW, H0=NV_TH;',1)
    if module.count('export function rasterForecastTile(')!=1: raise ValueError('module export mismatch')
    c=c.replace('function nvPaintTile(',module.replace('export function','function',1)+'\nfunction nvPaintTile(',1)
    out=c.encode('utf8');name='ms_r5_perf_core_'+sha(out)[:16]+'.js'
    ref=('<script src="/assets/'+CORE+'"></script>').encode()
    if index.count(ref)!=1: raise ValueError('core reference mismatch')
    return index.replace(ref,('<script src="/assets/'+name+'"></script>').encode(),1),out,name
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw):return None
def fetch(path,limit):
    req=urllib.request.Request('https://wtafkik.ir'+path,headers={'Accept-Encoding':'identity','Cache-Control':'no-cache'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=45) as r:
        data=r.read(limit+1)
        if r.status!=200 or len(data)>limit:raise ValueError('live fetch failed')
        return data
if __name__=='__main__':
    z=Path('v88-artifact/MetStat_V88_upload.zip')
    if sha(z.read_bytes())!=ZIP_SHA:raise ValueError('unexpected artifact hash')
    i,c,n,_=inspect_zip(z)
    if n!='assets/'+CORE:raise ValueError('unexpected V88 filename')
    base=Path('v89-baseline');(base/'assets').mkdir(parents=True,exist_ok=True);(base/'index.html').write_bytes(i);(base/n).write_bytes(c)
    live=fetch('/',2_000_000)
    approved={'0adaeabb312653692ba463a0bc6c0d24e19a79d9c125ed53aed59eea809ed785':('V87','4a4e77930c1b17d3','4a4e77930c1b17d3fc39353d32d3c88ac9691edb69d108f84718c1ae49eb239e'),INDEX_SHA:('V88',CORE_SHA[:16],CORE_SHA)}
    if sha(live) not in approved:raise ValueError('unknown live HTML; no release')
    version,prefix,expected=approved[sha(live)]
    if sha(fetch('/assets/ms_r5_perf_core_'+prefix+'.js',6_000_000))!=expected:raise ValueError('unknown live core; no release')
    Path('v89-live-baseline.json').write_text(json.dumps({'version':version,'index_sha256':sha(live),'core_sha256':expected}))
    Path('v89-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    i,c,n=build(i,c,(Path(__file__).resolve().parents[1]/'web/forecast/tile-raster.mjs').read_text(encoding='utf8'))
    out=Path('v89-candidate');(out/'assets').mkdir(parents=True,exist_ok=True);(out/'index.html').write_bytes(i);(out/'assets'/n).write_bytes(c)
    print(sha(i),n,sha(c))
