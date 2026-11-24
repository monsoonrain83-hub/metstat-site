#!/usr/bin/env python3
"""Minimal, pinned R5 *reference preview* fix: horizontal access on phones.

Does not touch the live site, Stage22, Stage29, map data or assets.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import sys

REFERENCE_SHA256 = "2792e674660f07135acb91f6cbf92f8740f4c9ff8c073e94767927b1c8dbadf9"
ORIGINAL = b'@media(max-width:650px) and (orientation:portrait){.app{min-width:960px}}'
REVISED = b'@media(max-width:650px) and (orientation:portrait){.app{min-width:960px}body{min-width:960px}}'


def patch(data: bytes, expected_sha256: str = REFERENCE_SHA256) -> bytes:
    if sha256(data).hexdigest() != expected_sha256:
        raise ValueError("R5 source drift: abort instead of modifying unknown HTML")
    if data.count(ORIGINAL) != 1 or REVISED in data:
        raise ValueError("R5 portrait style marker absent or duplicated")
    return data.replace(ORIGINAL, REVISED, 1)


def main(argv=None) -> int:
    ap = ArgumentParser()
    ap.add_argument("reference", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args(argv)
    if args.reference.resolve() == args.output.resolve():
        ap.error("Output must be a distinct staging file")
    try:
        data = args.reference.read_bytes()
        result = patch(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(result)
    except (ValueError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, "not_live": True,
                      "before_sha256": sha256(data).hexdigest(),
                      "after_sha256": sha256(result).hexdigest(),
                      "change": "portrait-only body min-width for RTL horizontal scrolling"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
