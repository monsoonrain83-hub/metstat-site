"""Replace sidebar rendering blocks with canonical tested modules, exact V86 only."""
from pathlib import Path
import hashlib, urllib.request
ROOT=Path(__file__).resolve().parent
CORE='ms_r5_perf_core_6b336b595a78ab27.js'
INDEX_SHA='cd083069158621a4844196bcad1362bfea95e3aa8836a88525ab741b9fbdbca4'
CORE_SHA='6b336b595a78ab27429cf99844008f8e5a499ea0857cf25fbd01aeebba889112'
def sha(b):return hashlib.sha256(b).hexdigest()
def replace(s,a,b):
    if s.count(a)!=1:raise ValueError('anchor mismatch: '+a[:120])
    return s.replace(a,b,1)
def module(path,fn):
    s=path.read_text(encoding='utf8')
    return replace(s,'export function '+fn+'(', 'function '+fn+'(')
def build(index,core,modroot):
    if sha(index)!=INDEX_SHA or sha(core)!=CORE_SHA:raise ValueError('V86 baseline mismatch')
    c=core.decode('utf8');a=c.index('function nvrParamRender(){');b=c.index('function nvrShort(',a)
    if c.count('function nvrParamRender(){')!=1:raise ValueError('duplicate picker')
    modules=module(modroot/'parameter-picker.mjs','createParameterPicker')+'\n'+module(modroot/'sidebar-controls.mjs','createSidebarControls')
    bridge='''const NVR_PARAM_RENDER=createParameterPicker(), NVR_CONTROLS=createSidebarControls();
function nvrParamRender(){
  const host=document.getElementById("msR5ParamPicker");if(!host||!ON.man)return;
  NVR.grp=NVR_PARAM_RENDER(host,{parameters:nvParamsOf(NV.s.m),categories:ON.man.cats||[],secondary:NV.s.cat==="sc",selected:NV.s.p,group:NVR.grp,secondaryGroups:NV_SEC_GROUPS,text:msR5T,translate:tr});
}

'''
    c=c[:a]+modules+'\n'+bridge+c[b:]
    a=c.index('  mirrors.forEach(s=>{ const o=g(s.dataset.mir)',c.index('function nvrSync(force)'))
    b=c.index('\n  const periods=',a)
    if 's.innerHTML=' not in c[a:b]:raise ValueError('mirror anchor mismatch')
    c=c[:a]+'''  mirrors.forEach(s=>{ const o=g(s.dataset.mir), id=s.dataset.mir; NVR_CONTROLS.options(s,[...o.options].map((q,i)=>({value:q.value,label:nvrShort(id,q,i),disabled:q.disabled})),o.value); const title=o.selectedOptions[0]?o.selectedOptions[0].textContent:""; if(s.title!==title)s.title=title; });'''+c[b:]
    a=c.index('  if(periods){periods.replaceChildren();',c.index('function nvrSync(force)'));b=c.index('  nvrParamRender();',a)
    if 'if(modelRows){modelRows.replaceChildren();' not in c[a:b]:raise ValueError('model row anchor mismatch')
    c=c[:a]+'''  if(periods)NVR_CONTROLS.periods(periods,[...$("nvTc").options],$("nvTc").value,LANG==="en"?{daily:"Daily",weekly:"Weekly",monthly:"Monthly",seasonal:"Seasonal",ens:"Ensemble"}:{daily:"روزانه",weekly:"هفتگی",monthly:"ماهانه",seasonal:"فصلی",ens:"انسمبل"});
  if(modelRows)NVR_CONTROLS.models(modelRows,[...$("nvM").options],$("nvM").value);
'''+c[b:]
    a=c.index('const keep=opts.filter(o=>(o.value==="sc")===isS);',c.index('function nvrSync(force)'));b=c.index('\n  /* فعال',a)
    if '$("nvX5").innerHTML=' not in c[a:b]:raise ValueError('category anchor mismatch')
    c=c[:a]+'''const keep=opts.filter(o=>(o.value==="sc")===isS); NVR_CONTROLS.options($("nvX5"),keep.map(o=>({value:o.value,label:o.textContent,disabled:o.disabled})),cat.value);'''+c[b:]
    c=replace(c,'''e.classList.remove("ms-g","ms-b","ms-r"); if(st) e.classList.add(st);''','''for(const cls of ["ms-g","ms-b","ms-r"])if(cls!==st&&e.classList.contains(cls))e.classList.remove(cls); if(st&&!e.classList.contains(st))e.classList.add(st);''')
    if c.count('function createParameterPicker(')!=1 or c.count('function createSidebarControls(')!=1:raise ValueError('duplicate owner')
    out=c.encode('utf8');name='ms_r5_perf_core_'+sha(out)[:16]+'.js';ref=('<script src="/assets/'+CORE+'"></script>').encode()
    if index.count(ref)!=1:raise ValueError('HTML reference mismatch')
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
    base=Path('v87-baseline')
    i,c=fetch('/',2_000_000,INDEX_SHA),fetch('/assets/'+CORE,6_000_000,CORE_SHA)
    (base/'assets').mkdir(parents=True,exist_ok=True);(base/'index.html').write_bytes(i);(base/'assets'/CORE).write_bytes(c)
    Path('v87-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    i,c,n=build(i,c,ROOT.parent/'web/forecast');out=Path('v87-candidate');(out/'assets').mkdir(parents=True,exist_ok=True);(out/'index.html').write_bytes(i);(out/'assets'/n).write_bytes(c)
    print(sha(i),n,sha(c))
