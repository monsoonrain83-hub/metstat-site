#!/usr/bin/env python3
"""Exact source-pinned Stage37 native viewer recovery patch (no host deployment)."""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import re

SOURCE_SHA = "f594a4aabdf8f77fe4dd17c8bd0b73fd39102830830a440f5c151445cdcd3893"
TARGET_SHA = "a6ee0843b29c300ec083ef0d7c636eb759ee4dd3eb9ea90d38079d5240243aa1"

PATCHES = (
    (
        '''  const p=new Promise(res=>{ const im=new Image(); im.onload=()=>res(im); im.onerror=()=>res(null); im.src=url; });
  NV.cache.set(url,p); if(NV.cache.size>60){ const k=NV.cache.keys().next().value; NV.cache.delete(k); } return p;''',
        '''  const p=new Promise(res=>{ const im=new Image(); im.onload=()=>res(im); im.onerror=()=>res(null); im.src=url; }).then(img=>{
    // An unsuccessful request is NOT evidence the model frame is permanently unavailable.
    // Keep successful shared promises, but permit a genuine retry after a transient 404/network error.
    if(!img && NV.cache.get(url)===p) NV.cache.delete(url);
    return img;
  });
  NV.cache.set(url,p); if(NV.cache.size>60){ const k=NV.cache.keys().next().value; NV.cache.delete(k); } return p;''',
    ),
    (
        '''  if(!cur){ NV.entry=null; $("nvTitle").textContent=ON.man&&ON.man.items&&ON.man.items.length?"نقشه‌ای برای این انتخاب نیست":"—"; $("nvSub").textContent=""; nvDraw(); return; }''',
        '''  if(!cur){
    // This may supersede an in-flight request; the superseded promise exits on its token.
    NV.busy=false; const pending=$("nvBusy"); if(pending) pending.hidden=true;
    NV.entry=null; $("nvTitle").textContent=ON.man&&ON.man.items&&ON.man.items.length?"نقشه‌ای برای این انتخاب نیست":"—"; $("nvSub").textContent=""; nvDraw(); return;
  }''',
    ),
)


def sha(blob: bytes) -> str:
    return sha256(blob).hexdigest()


def scripts(blob: str) -> list[str]:
    return re.findall(r"<script\b[^>]*>(.*?)</script\s*>", blob, re.I | re.S)


def styles(blob: str) -> list[str]:
    return re.findall(r"<style\b[^>]*>(.*?)</style\s*>", blob, re.I | re.S)


def apply(blob: bytes, *, source_sha: str = SOURCE_SHA, target_sha: str | None = TARGET_SHA) -> bytes:
    if sha(blob) != source_sha:
        raise ValueError("Refusing unknown or already patched active host index SHA")
    original = blob.decode("utf-8")
    text = original
    for before, after in PATCHES:
        if text.count(before) != 1:
            raise ValueError("Anchor missing, ambiguous or already applied")
        text = text.replace(before, after, 1)
    prev_scripts, next_scripts = scripts(original), scripts(text)
    if len(prev_scripts) != len(next_scripts):
        raise ValueError("Script count changed")
    if [i for i, (a, b) in enumerate(zip(prev_scripts, next_scripts)) if a != b] != [11]:
        raise ValueError("Unexpected script owner modified")
    if styles(original) != styles(text) or text.count("!important") != original.count("!important"):
        raise ValueError("Style/CSS changed unexpectedly")
    if any(text.count(marker) != 1 for marker in ('id="onEmpty"', 'id="onViewer" hidden', 'id="onAside"')):
        raise ValueError("Protected viewer IDs changed unexpectedly")
    result = text.encode("utf-8")
    if target_sha is not None and sha(result) != target_sha:
        raise ValueError("Candidate SHA mismatch; release is not approved")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Make a Stage37 candidate from an exact Stage36 file; no cPanel upload")
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    ns = p.parse_args()
    if ns.source.resolve() == ns.output.resolve():
        p.error("Source and output must differ")
    if not ns.source.is_file() or ns.source.stat().st_size > 16 * 1024 * 1024:
        p.error("Missing or oversized source")
    candidate = apply(ns.source.read_bytes())
    with ns.output.open("xb") as out:
        out.write(candidate)
    print(f"Candidate only: {ns.output} SHA256={sha(candidate)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
