#!/usr/bin/env python3
"""Stage40 deterministic Atlas-only patch from exact Stage39 host HTML.

No network, deployment, data generation or in-place overwrite.
"""
import argparse
import hashlib
import re
from pathlib import Path

SOURCE_SHA='9dc68b50c2e8817e8e1b9996d8fd7d48f6defd016aca0a8cdd9a10c949d93e0e'
TARGET_SHA='3b80f0e8db2334e1e0a0febe3acd17f84ba89dcac09b2f1632353f61d8859958'
BEFORE='''/* Native climate atlas is NOT three columns: the original two control
   panels share one right-side scroll region; chart/map stays to the left. */
html.ms9-active #caApp>aside{grid-column:1;grid-row:1;display:block;min-width:0;max-width:100%;overflow-x:hidden}
html.ms9-active #caApp>main{grid-column:2;grid-row:1;min-width:0;width:100%;max-width:100%}'''
AFTER='''/* Atlas: preserve BOTH native settings asides (#caAside, dynamically inserted
   #caAside2) IN SOURCE ORDER in the right track, without overlap. Real output
   stays in the left track. Force grid also below 981px: no mobile stacking. */
html.ms9-active #caApp.wrap:not([hidden]){display:grid;grid-template-columns:var(--ms9-sidebar-width,328px) minmax(0,1fr);grid-template-rows:auto auto;align-content:start;align-items:start;gap:12px;min-width:0;max-width:100%;direction:rtl}
html.ms9-active #caApp>aside#caAside,
html.ms9-active #caApp>aside#caAside2{grid-column:1;display:grid;grid-template-columns:minmax(0,1fr);gap:12px;position:static;max-height:none;min-width:0;max-width:100%;width:100%;overflow:visible;align-self:start;order:0}
html.ms9-active #caApp>aside#caAside{grid-row:1}
html.ms9-active #caApp>aside#caAside2{grid-row:2}
html.ms9-active #caApp>main{grid-column:2;grid-row:1/span 2;min-width:0;width:100%;max-width:100%;order:0;overflow-x:auto}
html.ms9-active #caApp>.caAsideTgl{display:none}
html.ms9-active #caApp #caEmpty:not([hidden]){display:block}
html.ms9-active #caApp>aside .panel{min-width:0;max-width:100%;box-sizing:border-box}
html.ms9-active #caApp>aside :is(input,select,textarea,button){max-width:100%;box-sizing:border-box}'''
OLD_REVEAL='function caMobileReveal(){ try{ if(window.matchMedia&&matchMedia("(max-width:980px)").matches){'
NEW_REVEAL='function caMobileReveal(){ try{ if(document.documentElement.classList.contains("ms9-active")) return; if(window.matchMedia&&matchMedia("(max-width:980px)").matches){'
OLD_COLLAPSE='function caCollapse(){ if(innerWidth>=981) return;'
NEW_COLLAPSE='function caCollapse(){ if(document.documentElement.classList.contains("ms9-active") || innerWidth>=981) return;'


def sha(buf):
    return hashlib.sha256(buf).hexdigest()


def apply(source, *, source_sha=SOURCE_SHA, target_sha=TARGET_SHA):
    if sha(source) != source_sha:
        raise ValueError('Unrecognized Stage39 source SHA; refuse host overwrite')
    src=source.decode('utf-8','strict')
    position=src.index('<style id="ms9-desktop-r5-system">')
    end=src.index('</style>',position)
    if not position < src.index(BEFORE) < end:
        raise ValueError('Atlas anchor not in original R5 style owner')
    out=src
    for before,after in ((BEFORE,AFTER),(OLD_REVEAL,NEW_REVEAL),
                         (OLD_COLLAPSE,NEW_COLLAPSE)):
        if out.count(before)!=1:
            raise ValueError('Patch anchor is missing or repeated')
        out=out.replace(before,after,1)
    if src.count('!important')!=out.count('!important'):
        raise ValueError('Unexpected CSS-priority mutation')
    prior=re.findall(r'<script\b[^>]*>(.*?)</script\s*>',src,re.I|re.S)
    after=re.findall(r'<script\b[^>]*>(.*?)</script\s*>',out,re.I|re.S)
    if len(prior)!=len(after) or [i for i,(a,b) in enumerate(zip(prior,after)) if a!=b]!=[11]:
        raise ValueError('Unexpected script ownership change')
    result=out.encode('utf-8')
    if target_sha and sha(result)!=target_sha:
        raise ValueError('Unapproved candidate SHA')
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path)
    p.add_argument('target',type=Path)
    a=p.parse_args()
    if a.source.resolve()==a.target.resolve():
        p.error('Do not overwrite source')
    candidate=apply(a.source.read_bytes())
    with a.target.open('xb') as fh:
        fh.write(candidate)
    print('Candidate-only',str(a.target),sha(candidate))


if __name__=='__main__':
    main()
