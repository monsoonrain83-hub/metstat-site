#!/usr/bin/env python3
"""Read-only Stage22 -> Stage29 cPanel candidate install gate.

Usage: python tools/metstat_stage29_host_preflight.py /path/to/unzipped/public_html
This NEVER writes/deletes or copies into cPanel. It aborts on version drift.
"""
from __future__ import annotations

from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import sys

STAGE22 = {
    "index.html": "339f863f863aef5a33e5567c5ec03d06a57fe9da8ad3ba908e62d2e4e73c44cb",
    "assets/metstat_map_ui_r201.js": "9e89b968db5b3ac3287aa0228d5111a855c7afe4c9f92ee0b3d0f9aae88ed01a",
}
PINNED = {
    "online/station_isohyet_v26.html": "faae6460663df2170a68898c51f1e19f9a7f80080dacd7cc8f106a8f25cec629",
    "online/meteo_toolbox_v22.html": "7d2037068e621e79925ab6b64a5cba5232773fed450f62e826b534e98d930d87",
    "online/forecast_verification_v22.html": "8393def632f1adb74fa81ee9649f6c7092a1a569fb7918edee2a820f1e5a841c",
    "online/bulletin_maps_v21.html": "081145bec35d883c1cd5a398823ac45bd50fa97f64361d9a56b79b38ecc2e6bd",
    "assets/map_layers.js": "b32b491c7105f77c7d23767dd8773f37edb9eda480b9067a2ace6f4d616380b8",
    "online/atlas_stations_v28.json": "b121614b0addf69ec4bb3b4b7b8f9f031f773e69c5a35c7ecc58f05bf48b733d",
}
OPTIONAL_BASE = {
    "assets/metstat_map_ui_r201.css": "129c08eea0ec16dda407b5f2124ff325787a0b49eaffe7a7afc7e545b8f23940",
    "assets/metstat_r5_stage23_restore.css": "e7930ff3b2fb92166496f98a7007a35b2c8f9c7b55324c7045ea1ababdad1cb5",
    "assets/metstat_r5_stage24_restore.js": "19c9954f3540a52bb6f83f81794b7f3ccf7b8978bf38ed2393666c78ae2af1f5",
}


def scan(root: Path) -> dict:
    root = root.resolve(strict=True)
    issues = []
    checked = 0
    for path, expected in {**STAGE22, **PINNED, **OPTIONAL_BASE}.items():
        original = root / path
        # A staged root must consist of regular files, not mutable symlink aliases.
        # Check every path component before resolving, including dangling links.
        if any(part.is_symlink() for part in (original, *original.parents) if part != root and part.is_relative_to(root)):
            issues.append({"path": path, "problem": "symlink-not-allowed"})
            continue
        full = original.resolve()
        if not full.is_relative_to(root):
            issues.append({"path": path, "problem": "escaped-root"})
            continue
        if not full.exists() and path in OPTIONAL_BASE:
            continue
        if not full.is_file():
            issues.append({"path": path, "problem": "missing"})
            continue
        # Stream large source/engine files rather than loading them entirely into RAM.
        digest = hashlib.sha256()
        try:
            with full.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError as exc:
            issues.append({"path": path, "problem": "unreadable", "error": type(exc).__name__})
            continue
        actual = digest.hexdigest()
        checked += 1
        if actual != expected:
            issues.append({"path": path, "problem": "unexpected-version",
                           "expected": expected, "actual": actual})
    return {
        "read_only": True, "source": "Stage22", "active_cpanel_verified": False,
        "checked": checked, "ok": len(issues) == 0, "issues": issues,
        "note": "Review SHA drift before any overwrite; back up outside public_html and validate staging HTTPS first."
    }


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("document_root", type=Path)
    args = parser.parse_args()
    report = scan(args.document_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
