#!/usr/bin/env python3
"""Rebuild only the exact Stage41 candidate from a SHA-verified Stage40 host index.

No web writes, no data changes, no cPanel credentials. Reject source drift.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import re

SOURCE_SHA='3b80f0e8db2334e1e0a0febe3acd17f84ba89dcac09b2f1632353f61d8859958'
TARGET_SHA='7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295'
ATLAS_OLD='for(const h of document.querySelectorAll("#caApp .panel>h2")) if(!h.dataset.tg){ h.dataset.tg=1; h.onclick=()=>h.parentNode.classList.toggle("pcol"); }'
ATLAS_NEW='''for(const h of document.querySelectorAll("#caApp .panel>h2")) if(!h.dataset.tg){
    h.dataset.tg="1"; h.tabIndex=0; h.setAttribute("role","button");
    const sync=()=>h.setAttribute("aria-expanded",String(!h.parentNode.classList.contains("pcol")));
    const toggle=()=>{ h.parentNode.classList.toggle("pcol"); sync(); };
    h.onclick=toggle;
    h.onkeydown=e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); toggle(); } };
    sync();
  }'''
SF_OLD='''SF.col=SF.col||{}; m.querySelectorAll(".card>h3").forEach(h=>{ const c=h.parentNode, key=h.textContent.trim().slice(0,30), keepOpen=!!c.querySelector("#sfView"); const st=key in SF.col?SF.col[key]:!keepOpen; c.classList.toggle("pcol",st); h.onclick=()=>{ const v=c.classList.toggle("pcol"); SF.col[key]=v; }; h.title=SFT("جمع/باز کردن","Collapse / expand"); });'''
SF_NEW='''SF.col=SF.col||{}; m.querySelectorAll(".card>h3").forEach((h,i)=>{
    const c=h.parentNode;
    // Stable semantic keys: toggles survive fa/en and redraw (not translated headings).
    const key=c.classList.contains("sfSet")?"settings":c.querySelector("#sfIdxTab")?"indices":c.querySelector("#sfView")?"forecast":c.querySelector("#sfViewC")?"scenario":c.parentNode.classList.contains("sfSide")?"method":"panel-"+i;
    // Essential right-side controls and the primary left-side forecast start expanded.
    const st=Object.prototype.hasOwnProperty.call(SF.col,key)?SF.col[key]:!(key==="settings"||key==="forecast");
    c.classList.toggle("pcol",st);
    h.tabIndex=0; h.setAttribute("role","button");
    const sync=()=>h.setAttribute("aria-expanded",String(!c.classList.contains("pcol")));
    const toggle=()=>{ const v=c.classList.toggle("pcol"); SF.col[key]=v; sync(); };
    h.onclick=toggle;
    h.onkeydown=e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); toggle(); } };
    h.title=SFT("جمع/باز کردن","Collapse / expand"); sync();
  });'''
CSS_NEW='''/* R5: true keyboard focus on the ORIGINAL Atlas/seasonal disclosure headings.
   No duplicate button; source controllers remain single-owner. */
html.ms9-active #caApp .panel>h2:focus-visible,
html.ms9-active #sfMain .card>h3:focus-visible{outline:2px solid #205d9a;outline-offset:3px;border-radius:6px}
'''


def sha(buf: bytes) -> str:
    return sha256(buf).hexdigest()


def parts(html: str, tag: str) -> list[str]:
    return re.findall(r"<"+tag+r"\b[^>]*>(.*?)</"+tag+r"\s*>", html, re.I|re.S)


def patch(blob: bytes, *, source_sha: str = SOURCE_SHA,
          target_sha: str | None = TARGET_SHA) -> bytes:
    if sha(blob) != source_sha:
        raise ValueError("Unknown, newer or already patched host index: refuse")
    old=blob.decode("utf8", "strict")
    new=old
    for before,after in ((ATLAS_OLD,ATLAS_NEW),(SF_OLD,SF_NEW)):
        if new.count(before)!=1:
            raise ValueError("Expected unique native control owner is missing")
        new=new.replace(before,after,1)
    owner='<style id="ms9-desktop-r5-system">'
    if new.count(owner)!=1:
        raise ValueError("R5 style owner missing")
    at=new.index(owner)+len(owner)
    new=new[:at]+'\n'+CSS_NEW+new[at:]
    js_old,js_new=parts(old,'script'),parts(new,'script')
    css_old,css_new=parts(old,'style'),parts(new,'style')
    if len(js_old)!=len(js_new) or [i for i,(a,b) in enumerate(zip(js_old,js_new)) if a!=b]!=[11]:
        raise ValueError("Changed unexpected JS script owner")
    if len(css_old)!=len(css_new) or [i for i,(a,b) in enumerate(zip(css_old,css_new)) if a!=b]!=[5]:
        raise ValueError("Changed unexpected CSS style owner")
    if old.count('!important')!=new.count('!important'):
        raise ValueError("CSS priority count changed")
    for marker in ('id="caAside"','id="sfMain"','id="caCards"','id="caApp"'):
        if old.count(marker)!=new.count(marker):
            raise ValueError("Protected native DOM changed")
    answer=new.encode('utf8')
    if target_sha is not None and sha(answer)!=target_sha:
        raise ValueError("Candidate is not the approved Stage41 hash")
    return answer


def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path,help="Verified Stage40 index.html")
    p.add_argument("output",type=Path,help="A NEW candidate file (not in-place)")
    a=p.parse_args()
    if a.source.resolve()==a.output.resolve():
        p.error("Never overwrite input")
    raw=a.source.read_bytes()
    if len(raw)>16*1024*1024:
        p.error("Index exceeds size limit")
    result=patch(raw)
    with a.output.open("xb") as fh:
        fh.write(result)
    print("candidate-only",a.output,sha(result))


if __name__=="__main__":
    main()
