"""Small, independently testable menu computation optimization; no live deployment."""
from pathlib import Path
def patch(s):
    pairs=[('function nvMState(k){ try{ const o=ON.man.models[k], tc=((o.info&&o.info.tclass)||"daily"), G=nvModelsOf(tc).map(e=>e[1]).filter(x=>x&&x.run);','function nvMState(k,group){ try{ const o=ON.man.models[k], tc=((o.info&&o.info.tclass)||"daily"), G=group&&group.tc===tc?group.models:nvModelsOf(tc).map(e=>e[1]).filter(x=>x&&x.run);'),('const ms=nvModelsOf(NV.s.tc), al=ms.map(q=>q[0]), vis=all?ms:ms.filter(([k])=>nvModelHas(k)); return vis.map(([k,o])=>`<button','const ms=nvModelsOf(NV.s.tc), al=ms.map(q=>q[0]), vis=all?ms:ms.filter(([k])=>nvModelHas(k)), group={tc:NV.s.tc,models:ms.map(e=>e[1]).filter(x=>x&&x.run)}; return vis.map(([k,o])=>{ const st=nvMState(k,group); return `<button'),('${nvMState(k)}${k===NV.s.m?','${st}${k===NV.s.m?'),('[nvMState(k)]||""','[st]||""'),('${nvLabU(k,o,al)}</button>`).join("")','${nvLabU(k,o,al)}</button>`; }).join("")')]
    for a,b in pairs:
        if s.count(a)!=1: raise ValueError('anchor mismatch: '+a[:80])
        s=s.replace(a,b,1)
    return s
if __name__=='__main__':
    import sys
    src=Path(sys.argv[1]); dest=Path(sys.argv[2])
    dest.write_text(patch(src.read_text(encoding='utf-8')),encoding='utf-8')
