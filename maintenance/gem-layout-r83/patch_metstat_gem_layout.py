#!/usr/bin/env python3
"""Safe, deterministic MetStat GEM visibility + responsive layout patch.

Usage: python patch_metstat_gem_layout.py INPUT_INDEX_HTML OUTPUT_INDEX_HTML
Only modifies exact, known anchors. Never mutates original or private data.
"""
from pathlib import Path
import argparse, hashlib

MARKER='/* MetStat gem-display-layout-fix r83 */'
CSS=r'''<style>
/* MetStat gem-display-layout-fix r83 */
/* All changes scoped to the online model viewer and its controls. */
#onViewer .nvCard,#onViewer .nvTop,#onViewer .nvTime,#onViewer .nvTools,
#onViewer .nvPick,#onViewer .wx,#onViewer .wxBody,#onViewer .wxRow,
#onViewer .wxBar,#onAside .wx,#onAside .wxBody,#onAside .wxRow{
  min-width:0;max-width:100%;box-sizing:border-box;
}
#onViewer .wxChip,#onAside .wxChip{overflow-wrap:anywhere}
#onViewer .wxBar,#onViewer .wxRow,#onAside .wxRow{max-width:100%}
#onViewer .nvTop select,#onViewer .nvTime select,#onViewer .nvTools select,
#onAside select{min-width:0;max-width:100%;box-sizing:border-box}
.wxChip.ms-pending{opacity:.75;cursor:default!important;border:1px dashed #b8791e!important;
  background:#fff8e8!important;color:#7b4714!important;box-shadow:none!important}
@media(max-width:700px){
  #onViewer .nvR5{flex-wrap:wrap!important;min-width:0!important;max-width:100%!important;gap:5px!important}
  #onViewer .nvR5 input[type=range]{min-width:90px!important;flex:1 1 110px!important}
  #onViewer .nvR5 .btn.sm{min-width:0!important;white-space:normal!important;line-height:1.25!important}
  #onViewer .nvR5b>*{max-width:100%!important;min-width:0!important}
  #onViewer .nvTime,#onViewer .nvTop,#onViewer .nvTools{flex-wrap:wrap!important}
  #onViewer .wxRow.fr.wxGrid:not(.long) .wxChip{min-width:0!important;max-width:100%;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:clamp(10px,2.6vw,12.5px)}
  #onViewer .wxNav{max-width:100%;min-width:0;display:flex}
  #onViewer .wxNav .wxSel{flex:1 1 auto;min-width:0;max-width:100%}
  #onViewer .wxNav .wxArr{flex:0 0 38px;width:38px}
  .drFly{min-width:0!important;max-width:calc(100vw - 24px)!important;box-sizing:border-box}
}
</style>'''

def patch(text):
    if MARKER in text:
        raise ValueError('Already patched (r83 marker detected).')
    if text.count('</head>') != 1:
        raise ValueError('Unexpected HTML document: expected one </head> tag.')
    old_run = 'function nvRunSel(m){ const o=ON.man&&ON.man.models&&ON.man.models[m]; if(!o) return ""; const pv=nvRunPrev(m); return pv&&NV_RS[m]===pv.run?pv.run:o.run; }'
    new_run = '''function nvRunSel(m){
  const o=ON.man&&ON.man.models&&ON.man.models[m]; if(!o) return "";
  const pv=nvRunPrev(m);
  const live=(ON.man&&ON.man.items||[]).some(i=>i.m===m&&i.r==="me"&&!/L$/.test(i.p));
  const prev=!!pv&&(ON.man&&ON.man.items_prev||[]).some(i=>i.m===m&&i.r==="me"&&!/L$/.test(i.p));
  /* During a partial build, keep the available previous run. Never invent a tile. */
  if(!live&&prev) return pv.run;
  return pv&&NV_RS[m]===pv.run?pv.run:o.run;
}'''
    if text.count(old_run)!=1:
        raise ValueError('Cannot locate unique nvRunSel anchor; index.html likely differs from reviewed snapshot.')
    text=text.replace(old_run,new_run)
    old_chips = '''function wxModelChips(all){ const ms=nvModelsOf(NV.s.tc), al=ms.map(q=>q[0]), vis=all?ms:ms.filter(([k])=>nvModelHas(k)); return vis.map(([k,o])=>`<button type="button" class="wxChip wxM ${nvMState(k)}${k===NV.s.m?" on":""}" data-m="${k}" title="${({"ms-g":"اجرای جدید در حال ساخت","ms-b":"به‌روز و کامل","ms-r":"هنوز اجرای قبلی"})[nvMState(k)]||""}">${nvLabU(k,o,al)}</button>`).join("")||'<span class="hint">مدلی موجود نیست</span>'; }'''
    new_chips = '''function wxModelChips(all){
  const ms=nvModelsOf(NV.s.tc), al=ms.map(q=>q[0]);
  /* Keep available models visible even when another parameter/time is selected. */
  const vis=ms;
  let html=vis.map(([k,o])=>{
    const fallback=nvRunIsPrev(k)&&!(ON.man&&ON.man.items||[]).some(i=>i.m===k&&i.r==="me"&&!/L$/.test(i.p));
    const state=nvMState(k);
    const title=fallback?"نمایش اجرای قبلی؛ نقشهٔ فعلی هنوز آماده نیست":({"ms-g":"اجرای جدید در حال ساخت","ms-b":"به‌روز و کامل","ms-r":"هنوز اجرای قبلی"})[state]||"";
    return `<button type="button" class="wxChip wxM ${state}${k===NV.s.m?" on":""}" data-m="${k}" title="${title}">${nvLabU(k,o,al)}${fallback?" · قبلی":""}</button>`;
  }).join("");
  /* Report missing GEM honestly: selectable only when a real tile exists. */
  if(NV.s.tc==="daily"&&!ms.some(([k])=>String(k).toLowerCase()==="gem")){
    const listed=!!(ON.man&&ON.man.models&&ON.man.models.gem);
    html+=`<span class="wxChip wxM ms-pending" title="${listed?"GEM در مانیفست هست ولی نقشهٔ قابل استفاده برای خاورمیانه ندارد":"GEM در مانیفست فعلی سرور ثبت نشده است"}">GEM · ${listed?"منتظر نقشه":"فاقد داده"}</span>`;
  }
  return html||'<span class="hint">مدلی موجود نیست</span>';
}'''
    if text.count(old_chips)!=1:
        raise ValueError('Cannot locate unique wxModelChips anchor; index.html differs from reviewed snapshot.')
    text=text.replace(old_chips,new_chips)
    text=text.replace('</head>', CSS+'\n</head>',1)
    assert text.count(MARKER)==1
    return text

def main():
    a=argparse.ArgumentParser();a.add_argument('source');a.add_argument('target');args=a.parse_args()
    inp=Path(args.source);out=Path(args.target)
    original=inp.read_text(encoding='utf-8')
    result=patch(original)
    if inp.resolve()==out.resolve():raise ValueError('Source and destination must differ to avoid destructive overwrite')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(result,encoding='utf-8')
    print('BASE_SHA256',hashlib.sha256(original.encode()).hexdigest())
    print('OUTPUT_SHA256',hashlib.sha256(result.encode()).hexdigest())
    print('PATCHED_FILE',out)
if __name__=='__main__':main()
