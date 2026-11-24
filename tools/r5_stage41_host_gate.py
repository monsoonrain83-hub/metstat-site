#!/usr/bin/env python3
"""Stage41 ZIP validation gate for cPanel; strictly read-only and fail-closed.

Only approved host source index revisions may be upgraded. This tool checks
the archive, not the actual live PHP endpoints or NWP data.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile

SOURCE_SHA256 = {
    "original": "a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8",
    "stage37": "a6ee0843b29c300ec083ef0d7c636eb759ee4dd3eb9ea90d38079d5240243aa1",
    "stage39": "9dc68b50c2e8817e8e1b9996d8fd7d48f6defd016aca0a8cdd9a10c949d93e0e",
    "stage40": "3b80f0e8db2334e1e0a0febe3acd17f84ba89dcac09b2f1632353f61d8859958",
}
TARGET_SHA256 = "7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295"
ALLOWED_ASSETS = {
    "assets/metstat_map_ui_r201.js": "3a682ab3c43ca01fe5115ac7a1d5fbc5531d4fd8528429d91b5898bd28f7caf8",
    "assets/metstat_map_ui_r201.css": "b6b8ef2a9ad22a8956f77c9d4cba8e511d4e289faf3598fde0e20cad5e73a306",
    "assets/metstat_r5_stage24_restore.js": "7dd37b55e238372d80b2d0f8e124c291a56ef572986f28e97a36b75b36a41fb0",
}
LIMIT = 16 * 1024 * 1024


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)

    handle_startendtag = handle_starttag


def check(active_index: bytes, overlay: bytes, *,
          source_sha256: dict | None = None,
          target_sha256: str = TARGET_SHA256,
          expected_assets: dict | None = None) -> dict:
    """Never writes. Rejections must not be silently converted to deployment."""
    hashes = SOURCE_SHA256 if source_sha256 is None else source_sha256
    pinned_assets = ALLOWED_ASSETS if expected_assets is None else expected_assets
    baseline = sha(active_index)
    kind = next((k for k, value in hashes.items() if baseline == value), None)
    checks = {"active_index_pinned": kind is not None}
    files = {}
    try:
        with ZipFile(BytesIO(overlay)) as archive:
            names = archive.namelist()
            expected = {"index.html"} | (set(pinned_assets) if kind == "original" else set())
            checks["unique_zip_members"] = len(names) == len(set(names))
            checks["exact_expected_paths"] = set(names) == expected
            checks["size_cap"] = all(i.file_size <= LIMIT for i in archive.infolist())
            checks["zip_crc_ok"] = (
                archive.testzip() is None if all((checks[k] for k in
                    ("unique_zip_members", "exact_expected_paths", "size_cap"))) else False
            )
            if checks["zip_crc_ok"]:
                files = {n: archive.read(n) for n in expected}
    except (BadZipFile, OSError, ValueError, KeyError, RuntimeError):
        checks["zip_crc_ok"] = False
    candidate = files.get("index.html", b"")
    checks["candidate_index_sha"] = bool(candidate) and sha(candidate) == target_sha256
    checks["asset_shas"] = all(sha(files.get(n, b"")) == v for n, v in pinned_assets.items()) if kind == "original" else True
    checks["index_size"] = 1024 < len(candidate) <= LIMIT
    if candidate and checks["index_size"]:
        try:
            source = candidate.decode("utf-8")
            parser = Ids()
            parser.feed(source)
            checks["unique_dom_ids"] = not any(c > 1 for c in Counter(parser.ids).values())
            checks["required_native_nodes"] = all(source.count(token) == 1 for token in
                ('id="onEmpty"', 'id="onViewer" hidden', 'id="onAside"'))
            checks["stage37_events"] = source.count("metstat:nv-model-options") == 2 and (
                "document.addEventListener('langchange',syncGeo)" in source)
            checks["poll_removed"] = "setInterval(badgeModel,1800)" not in source
            checks["pointer_single_owner"] = "if(st.__msNvPointerBound) return;" in source
            checks["observer_leaves_clean"] = "NV.resizeObserver.disconnect(); NV.resizeObserver=null;" in source
            checks["no_fullscreen_label_poll"] = "setInterval(nvfBtnLab,600)" not in source
            checks["fullscreen_label_transitions"] = "NVF.on=true; nvfBtnLab();" in source and "NVF.on=false; nvfBtnLab();" in source
            checks["stage37_network_retry"] = (
                'if(!img && NV.cache.get(url)===p) NV.cache.delete(url);' in source)
            checks["stage37_empty_frame_clear"] = (
                'NV.busy=false; const pending=$("nvBusy"); if(pending) pending.hidden=true;' in source)
            checks["stage39_right_panel"] = (
                "grid-template-columns:var(--ms9-sidebar-width,328px) minmax(0,1fr)" in source
                and "--ms9-sidebar-width:230px" in source)
            checks["stage39_lab_synoptic"] = (
                "#labApp .lab>.labIn" in source
                and "#synApp .synCard" in source)
            checks["stage39_original_a11y_button"] = (
                "#fontBtn{position:fixed;inset-inline-end:4px;bottom:190px" in source)
            checks["stage39_no_atlas_three_columns"] = (
                "grid-template-columns:minmax(260px,310px) minmax(260px,310px) minmax(0,1fr)" not in source
                and "grid-template-columns:minmax(300px,340px) minmax(300px,340px) minmax(0,1fr)" not in source)
            checks["stage40_two_panel_source_rows"] = (
                "html.ms9-active #caApp.wrap:not([hidden]){display:grid;" in source
                and "#caApp>aside#caAside{grid-row:1}" in source
                and "#caApp>aside#caAside2{grid-row:2}" in source
                and "#caApp>main{grid-column:2;grid-row:1/span 2;" in source)
            checks["stage40_controls_visible_in_r5"] = (
                'function caMobileReveal(){ try{ if(document.documentElement.classList.contains("ms9-active")) return;' in source
                and 'function caCollapse(){ if(document.documentElement.classList.contains("ms9-active") || innerWidth>=981) return;' in source
                and "#caApp>.caAsideTgl{display:none}" in source)
            checks["stage40_empty_state_mobile"] = (
                "#caApp #caEmpty:not([hidden]){display:block}" in source)
            checks["stage41_accessible_native_atlas"] = (
                'h.setAttribute("role","button")' in source
                and 'h.onkeydown=e=>{ if(e.key==="Enter"||e.key===" ")' in source
                and 'aria-expanded' in source)
            checks["stage41_seasonal_semantic_keys"] = (
                'c.classList.contains("sfSet")?"settings"' in source
                and 'SF.col,key' in source
                and '!(key==="settings"||key==="forecast")' in source)
            checks["stage41_focus_visible"] = (
                'html.ms9-active #caApp .panel>h2:focus-visible' in source
                and 'html.ms9-active #sfMain .card>h3:focus-visible' in source)
            checks["no_added_important"] = source.count("!important") == 1138
        except UnicodeError:
            checks["valid_html_utf8"] = False
    else:
        checks["valid_html_utf8"] = False
    return {"pass": bool(checks) and all(v is True for v in checks.values()),
            "checks": checks, "source_kind": kind,
            "active_index_sha256": baseline,
            "candidate_index_sha256": sha(candidate) if candidate else None,
            "deployed": False}


def main() -> int:
    p = argparse.ArgumentParser(description="Offline verify one MetStat Stage41 host overlay; never deploy")
    p.add_argument("--active-index", type=Path, required=True)
    p.add_argument("--overlay", type=Path, required=True)
    args = p.parse_args()
    if not args.active_index.is_file() or args.active_index.stat().st_size > LIMIT:
        p.error("Current host index is absent or too large")
    if not args.overlay.is_file() or args.overlay.stat().st_size > LIMIT:
        p.error("Overlay archive absent or too large")
    result = check(args.active_index.read_bytes(), args.overlay.read_bytes())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
