#!/usr/bin/env python3
"""Replace existing R5 and native route-table entries; never append a new UI owner.

Input must be the actual user-supplied Stage41 index. Fail closed on any
hourly-automation or cPanel divergence. This is an offline generator only.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import re

SOURCE = "7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295"
TARGET = "51df572c1cb0a044a803933a31d2d76f355e6cd5912f4ddf955abb468834dec6"
CHANGES = (
    ('ap:()=>openAP(), apt:()=>openAP("tour")',
     'ap:()=>openAP("ov"), apt:()=>openAP("tour")'),
    ('apm:()=>openAP("mm"), ds:()=>openDS()',
     'apm:()=>openAP("mm"), warn72:()=>openAP("ex"), air:()=>openAP("exa"), earthquake:()=>openAP("exq"), ds:()=>openDS()'),
    ("'mtn','apt','aph','syn','ca'",
     "'mtn','apt','aph','warn72','air','earthquake','syn','ca'"),
)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def scripts(txt: str) -> list[str]:
    return re.findall(r'<script\b[^>]*>(.*?)</script\s*>', txt, re.S | re.I)


def build(source: bytes, *, source_sha: str = SOURCE, target_sha: str | None = TARGET) -> bytes:
    if digest(source) != source_sha:
        raise ValueError("Active R5 source has changed; refuse overwrite/patch")
    old = source.decode("utf8", errors="strict")
    new = old
    for previous, replacement in CHANGES:
        if new.count(previous) != 1:
            raise ValueError("Native route-owner token missing or duplicated")
        new = new.replace(previous, replacement, 1)
    first, second = scripts(old), scripts(new)
    if len(first) != 19 or len(second) != 19:
        raise ValueError("Unexpected native script count")
    if [i for i, (a, b) in enumerate(zip(first, second)) if a != b] != [11, 14]:
        raise ValueError("Attempted to change a different script owner")
    without_scripts = lambda txt: re.sub(
        r'<script\b[^>]*>.*?</script\s*>', '', txt, flags=re.S | re.I
    )
    if without_scripts(old) != without_scripts(new):
        raise ValueError("Changed HTML, CSS, scripts or DOM outside the two native owners")
    if old.count("!important") != new.count("!important"):
        raise ValueError("Changed stylesheet priority")
    if old.count('id="apApp"') != new.count('id="apApp"') or 'id="apApp"' not in new:
        raise ValueError("Changed or cloned the application page")
    if new.count("const mapped=new Set") != 1:
        raise ValueError("Multiple R5 navigation owners")
    raw = new.encode("utf8")
    if target_sha and digest(raw) != target_sha:
        raise ValueError("Unapproved or unexpected candidate checksum")
    return raw


def main() -> int:
    p = argparse.ArgumentParser(description="Offline native R5 route table repair")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    if args.input.resolve() == args.output.resolve():
        p.error("In-place write is forbidden")
    if args.input.stat().st_size > 16_000_000:
        p.error("Unexpected large host index")
    corrected = build(args.input.read_bytes())
    with args.output.open("xb") as file:
        file.write(corrected)
    print(digest(corrected), "candidate-only (not published)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
