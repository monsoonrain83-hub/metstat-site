"""Reconstruct V81 from exact verified public V80 assets. No host writes."""
from pathlib import Path
import hashlib
import urllib.request
import zipfile

BASE='https://wtafkik.ir'
CORE='ms_r5_perf_core_5bf9868a04910eee.js'
INDEX_SHA='4aacde5aaf85930180453c91c915791c21d848ee3abae145acd086029fd9a8db'
CORE_SHA='5bf9868a04910eee68c29c37f8a701932fd1c9f11c55c805d79234539f190c8a'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ValueError('unexpected redirect')

def digest(data): return hashlib.sha256(data).hexdigest()

def fetch(path,sha,limit):
    req=urllib.request.Request(BASE+path,headers={'Accept-Encoding':'identity','Cache-Control':'no-cache','User-Agent':'MetStat-V81-verification/1.0'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=45) as r:
        data=r.read(limit+1)
        if r.status!=200 or len(data)>limit or digest(data)!=sha:
            raise ValueError('live baseline mismatch: '+path)
        return data.decode('utf-8')

def patch(t,a,b):
    if t.count(a)!=1: raise ValueError('patch anchor mismatch: '+a[:100])
    return t.replace(a,b,1)

def build(s,c):
    s=patch(s,'window.addEventListener("load",function(){setTimeout(function(){try{wuzLoad()}catch(e){}try{ttOvLoad()}catch(e){}},1500)});','/* V81: optional overlays load at their actual consumers, not on every page. */')
    c=patch(c,'const n=wuZoomName(z); let im=n&&WU_ZOOM_IMG[n];','const n=wuZoomName(z); if(n&&!_wuzP&&_wuzTry<3) wuzLoad(); let im=n&&WU_ZOOM_IMG[n];')
    c=patch(c,'wuzInit(); try{ if(typeof wuzSync==="function") wuzSync(); }catch(e){} }).catch(e=>','wuzInit(); try{ if(typeof wuzSync==="function") wuzSync(); }catch(e){} Promise.all(Object.values(WU_ZOOM_IMG).map(im=>im.decode().catch(()=>{}))).then(()=>{try{wuzRefresh()}catch(e){}}); }).catch(e=>')
    c=patch(c,'TT_OV_IMG.src=TT_OV_SRC; }).catch(()=>{ _ttP=null; })','TT_OV_IMG.src=TT_OV_SRC; return TT_OV_IMG.decode(); }).then(()=>{try{wuzRefresh()}catch(e){}}).catch(()=>{ _ttP=null; })')
    c=patch(c,'  // tropicaltidbits: خروجی هم‌اندازهٔ PNG مرزهای خاورمیانه (۳٫۶۶ برابر)\n','  // tropicaltidbits: خروجی هم‌اندازهٔ PNG مرزهای خاورمیانه (۳٫۶۶ برابر)\n  if(re && re.tt && P && P.custom && P.T && P.T.tt) await ttOvLoad();\n')
    c=patch(c,'  if((S.ttZoom||ttZoomSel())!=="iran") return false;','  if((S.ttZoom||ttZoomSel())!=="iran") return false;\n  if(S.showBorders && (brdMode()==="metstat"||brdMode()==="osm") && !_ttP) ttOvLoad();')
    c=patch(c,'  L.idx=L.frames.length-1; onLiveCard(); onLiveDraw(); onStatus("",1);','  if(J.raw) await wuZoomsReady();\n  L.idx=L.frames.length-1; onLiveCard(); onLiveDraw(); onStatus("",1);')
    h=digest(c.encode()); n='ms_r5_perf_core_'+h[:16]+'.js'
    s=patch(s,'<script src="/assets/'+CORE+'"></script>','<script src="/assets/'+n+'"></script>')
    return s,c,n

if __name__=='__main__':
    s=fetch('/',INDEX_SHA,2_000_000)
    c=fetch('/assets/'+CORE,CORE_SHA,6_000_000)
    s,c,n=build(s,c)
    root=Path('v81-candidate')
    (root/'assets').mkdir(parents=True,exist_ok=True)
    (root/'index.html').write_bytes(s.encode())
    (root/'assets'/n).write_bytes(c.encode())
    print('candidate:',digest(s.encode()),n,digest(c.encode()))
