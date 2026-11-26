"""V93: move three unchanged WeatherBELL raster layers out of the initial core.
Exact V92 source only; no host writes or scientific formula changes.
"""
import hashlib,base64,re,zipfile,json,runpy
from pathlib import Path
from verify_frontend_release import inspect_zip
def sha(b):return hashlib.sha256(b).hexdigest()
BASE_INDEX='054f9d61c2d418b66df078c3550b141416f3b6e9e01262b3b632243239cee770'
BASE_CORE='830b402e8c88464a550e6351e906e729a56650c2c54c4d972546d7cd7c9dc5fa'
BASE_ZIP='e9f6a92f8bf98ac423b22a3574cb61c1ffa892173efe788fbfea12d568cc0cc4'
NEXT_INDEX='e3087dd163fdcd114df595d8b71c8b229cffdd2e565acd6836853c90298cb5ad'
NEXT_CORE='13ff771e78308c226c9e93ece0c6e64ea8e1fbf7b40a5a1d031ff29ed674eb54'
LAYER_HASHES={'bold':'a44890a39baebfa9ff7518ac4434ec69601644baa723fa974dcb0258c9776206','orig':'cf309ba5758f85d976215373bcfe1be27c64642f85b1e9d0d871b7a49a77ae2c','grid':'79a8dbfb2bd2d46b62b00d01ffab9792a0e93a74af603f6e073fce8b38426125'}
def build(h,c):
    if sha(h)!=BASE_INDEX or sha(c)!=BASE_CORE:raise ValueError('unexpected V92 pair')
    s=c.decode();line=next(l for l in s.splitlines() if 'layers:{ bold:"data:image/png;base64,' in l)
    imgs={}
    def replace(m):
        k,b=m.groups();raw=base64.b64decode(b,validate=True);d=sha(raw)
        if LAYER_HASHES[k]!=d:raise ValueError('layer hash mismatch')
        name=f'assets/wb_layer_{k}_{d[:16]}.png';imgs[name]=raw;return f'{k}:"/{name}"'
    new=re.sub(r'(\w+):"data:image/png;base64,([A-Za-z0-9+/=]+)"',replace,line)
    if len(imgs)!=3 or s.count(line)!=1:raise ValueError('layer ownership mismatch')
    s=s.replace(line,new,1)
    a=s.index('    P.ov = {}; const bm = new Uint8Array(N);')
    b=s.index('    P.baseMask = bm;',a)+len('    P.baseMask = bm;')
    block='''    const owner=P, fw=FW, fh=FH, ov={}, bm=new Uint8Array(fw*fh);
    for(const [k,src] of Object.entries(owner.layers)){
      const im=new Image(); im.src=src; await im.decode();
      if(im.naturalWidth!==owner.W||im.naturalHeight!==owner.H) throw new Error("Invalid base layer dimensions");
      const c=document.createElement("canvas"); c.width=owner.W; c.height=owner.H;
      const cx=c.getContext("2d",{willReadFrequently:true}); cx.drawImage(im,0,0);
      const a=cx.getImageData(0,0,owner.W,owner.H).data;
      for(let y=0;y<fh;y++) for(let x=0;x<fw;x++) if(a[((y+owner.fy0)*owner.W+x+owner.fx0)*4+3]>0) bm[y*fw+x]=1;
      ov[k]=c;
    }
    // Publish only after all layers decode successfully. A failed request can be retried.
    owner.baseMask=bm; owner.ov=ov;'''
    s=s[:a]+block+s[b:];cb=s.encode();name='assets/ms_r5_perf_core_'+sha(cb)[:16]+'.js'
    oldname='assets/ms_r5_perf_core_'+BASE_CORE[:16]+'.js'
    if h.count(oldname.encode())!=1:raise ValueError('core ownership mismatch')
    nh=h.replace(oldname.encode(),name.encode(),1)
    if sha(nh)!=NEXT_INDEX or sha(cb)!=NEXT_CORE:raise ValueError('local/CI mismatch')
    return {'index.html':nh,name:cb,**imgs}
def write(root,files):
    for n,b in files.items():
        p=Path(root)/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
if __name__=='__main__':
    z=Path('v92-artifact/MetStat_V92_upload.zip')
    if sha(z.read_bytes())!=BASE_ZIP:raise ValueError('unexpected V92 ZIP')
    h,c,n,_=inspect_zip(z);write('v93-baseline',{'index.html':h,n:c})
    write('v93-candidate',build(h,c))
    fetch=runpy.run_path(str(Path(__file__).with_name('build-v89-tile-raster.py')))['fetch']
    approved={BASE_INDEX:BASE_CORE,'22368db76d7c67f4534f8abdf9de5f54eee1160777c56548bba1872c8de58a2c':'ee373baac9806769233f4c15a7c72887026e8b766a34f86a5e3af694be31f7a3'}
    live=sha(fetch('/',2_000_000))
    if live not in approved:raise ValueError('unrecognized live HTML')
    core=approved[live]
    if sha(fetch('/assets/ms_r5_perf_core_'+core[:16]+'.js',6_000_000))!=core:raise ValueError('live core mismatch')
    Path('v93-live-baseline.json').write_text(json.dumps({'index_sha256':live,'core_sha256':core}))
    Path('v93-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
