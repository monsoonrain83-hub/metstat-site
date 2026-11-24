#!/usr/bin/env python3
"""Fail-closed Stage33 MetStat HTML overlay preflight. Read-only; never deploys."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from zipfile import ZipFile

ORIGINAL = "a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8"
STAGE32 = "b3d7121fbdf99cfc838dc567bf4fc163bf64809d359031e5d2c06052ff0f432a"
STAGE33 = "4e4e0990df3d0f2a8bd4e503efdb7751cb724dd3e6e7f47e64b749d8eba5ce6b"
ASSET_SHA = {
    "assets/metstat_map_ui_r201.js": "3a682ab3c43ca01fe5115ac7a1d5fbc5531d4fd8528429d91b5898bd28f7caf8",
    "assets/metstat_map_ui_r201.css": "b6b8ef2a9ad22a8956f77c9d4cba8e511d4e289faf3598fde0e20cad5e73a306",
    "assets/metstat_r5_stage24_restore.js": "7dd37b55e238372d80b2d0f8e124c291a56ef572986f28e97a36b75b36a41fb0",
}
LIMIT = 16 * 1024 * 1024


class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, name, attrs):
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)

    handle_startendtag = handle_starttag


def sha(data):
    return sha256(data).hexdigest()


def checks(original, candidate, package, *, original_hash=ORIGINAL, stage32_hash=STAGE32, stage33_hash=STAGE33):
    """Returns checks without writing to disk; hash parameters are for isolated tests."""
    baseline_hash = sha(original)
    base_known = baseline_hash in (original_hash, stage32_hash)
    required = {"index.html"}
    if baseline_hash == original_hash:
        required.update(ASSET_SHA)
    candidate_hash = sha(candidate)
    scripts = lambda blob: re.findall(rb"<script\\b[^>]*>(.*?)</script\\s*>", blob, re.I | re.S)
    original_ids = IDs()
    original_ids.feed(original.decode("utf-8"))
    candidate_ids = IDs()
    candidate_ids.feed(candidate.decode("utf-8"))
    checks_map = {
        "baseline_pinned": base_known,
        "candidate_sha_pinned": candidate_hash == stage33_hash,
        "scripts_unchanged": scripts(original) == scripts(candidate) if baseline_hash == stage32_hash else None,
        "no_added_important_rules": candidate.count(b"!important") <= original.count(b"!important"),
        "no_new_duplicate_ids": not any(count > 1 for count in Counter(candidate_ids.ids).values()),
        "dom_id_count_unchanged": len(candidate_ids.ids) == len(original_ids.ids),
        "single_original_viewer": candidate.count(b'id="onViewer" hidden') == 1,
        "single_status_shell": candidate.count(b'id="onEmpty"') == 1 and b'ms33-r5-empty' in candidate,
    }
    if baseline_hash != stage32_hash:
        # Baseline Stage26 did not yet have Stage32's owner consolidation.
        checks_map.pop("scripts_unchanged")
    if package is not None:
        from io import BytesIO
        try:
            with ZipFile(BytesIO(package)) as z:
                names = z.namelist()
                no_duplicate = len(names) == len(set(names))
                no_paths = all(n == "index.html" or n in ASSET_SHA for n in names)
                size_ok = all(i.file_size <= LIMIT for i in z.infolist())
                crc_ok = z.testzip() is None if size_ok else False
                expected_set = set(names) == required
                sha_ok = sha(z.read("index.html")) == stage33_hash if expected_set and crc_ok else False
                assets_ok = all(sha(z.read(name)) == expected for name, expected in ASSET_SHA.items()) if baseline_hash == original_hash and expected_set and crc_ok else True
            checks_map.update(zip_unique=no_duplicate, zip_safe_paths=no_paths, zip_size_cap=size_ok, zip_crc=crc_ok, zip_members_expected=expected_set, zip_index_sha=sha_ok, zip_assets_pinned=assets_ok)
        except Exception:
            checks_map["zip_readable"] = False
    return {"passed": all(v is True for v in checks_map.values()), "checks": checks_map,
            "baseline": baseline_hash, "candidate": candidate_hash,
            "deployment": "not performed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--active-index", type=Path, required=True)
    ap.add_argument("--candidate-index", type=Path, required=True)
    ap.add_argument("--zip", type=Path, required=True)
    ns = ap.parse_args()
    try:
        report = checks(ns.active_index.read_bytes(), ns.candidate_index.read_bytes(), ns.zip.read_bytes())
    except (OSError, ValueError, UnicodeError) as exc:
        report = {"passed": False, "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
