#!/usr/bin/env python3
"""Rebuild a consolidated R5 staging ZIP, never deploy or delete live files.

Required inputs are explicitly supplied by the operator:
--stage26 MetStat_R5_STAGE26_FULL_STAGING.zip
--host-archive "file manager host.zip"

The archived backup is NOT the active Document Root. All archived engines,
model arrays, GIS geometry and payloads must remain byte-identical.
"""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup

CANONICAL_JS = "assets/metstat_map_ui_r201.js"
CANONICAL_CSS = "assets/metstat_map_ui_r201.css"
OLD_JS = "assets/metstat_r5_stage19_controls.js"
OLD_CSS = "assets/metstat_r5_stage19_controls.css"
MISSING = ("assets/metstat_original_model_chips_horizontal.js",
           "assets/metstat_original_model_chips_horizontal.css", CANONICAL_CSS)
REFERENCE = {
    "script": '<script defer src="' + OLD_JS + '?v=19" data-ms-stage19="1"></script>',
    "style": '<link rel="stylesheet" href="' + OLD_CSS + '?v=19" data-ms-stage19="1">',
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def make(stage26: Path, host_archive: Path, dest: Path):
    with zipfile.ZipFile(stage26) as archive:
        original = {name: archive.read(name) for name in archive.namelist()
                    if not name.endswith("/")}
    with zipfile.ZipFile(host_archive) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read("public html.zip"))) as public:
            with zipfile.ZipFile(io.BytesIO(public.read("assets.zip"))) as host:
                restored = {name: host.read(name) for name in MISSING}
    html = original["index.html"].decode("utf-8")
    assert all(html.count(v) == 1 for v in REFERENCE.values())
    assert CANONICAL_CSS not in original
    assert OLD_JS in original and OLD_CSS in original and CANONICAL_JS in original
    assert html.count("assets/metstat_map_ui_r201.js?v=201.5-r5asset1") == 1
    assert html.count("assets/metstat_map_ui_r201.css?v=201.0") == 1
    result = dict(original)
    # Script initialisation order is preserved. Both IIFEs still wait for DOM.
    result[CANONICAL_JS] += b"\n;\n" + result.pop(OLD_JS) + b"\n"
    # Only map-specific selectors are combined; no page layout rewrite.
    result[CANONICAL_CSS] = restored[CANONICAL_CSS] + b"\n" + result.pop(OLD_CSS)
    for name in MISSING:
        if name != CANONICAL_CSS:
            result[name] = restored[name]
    html = html.replace(REFERENCE["script"], "").replace(REFERENCE["style"], "")
    html = html.replace("assets/metstat_map_ui_r201.js?v=201.5-r5asset1",
                        "assets/metstat_map_ui_r201.js?v=201.6-r5owner")
    html = html.replace("assets/metstat_map_ui_r201.css?v=201.0",
                        "assets/metstat_map_ui_r201.css?v=201.6-r5owner")
    result["index.html"] = html.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    missing_refs = []
    for el in soup.select("script[src],link[href]"):
        url = el.get("src") or el.get("href") or ""
        if url.startswith(("assets/", "/assets/")):
            key = url.lstrip("/").split("?")[0]
            if key not in result:
                missing_refs.append(key)
    if missing_refs:
        raise ValueError("staging bundle missing local assets: " + repr(missing_refs))
    original_ids = [el.get("id") for el in soup.select("[id]")]
    if len(original_ids) != len(set(original_ids)):
        raise ValueError("duplicate DOM IDs")
    changed = {k for k in original if k in result and original[k] != result[k]}
    if changed != {"index.html", CANONICAL_JS}:
        raise ValueError("unexpected mutation: " + repr(changed))
    for k in ("online/station_isohyet_v26.html", "assets/map_layers.js",
              "online/atlas_stations_v28.json"):
        assert result[k] == original[k]
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        for name in sorted(result):
            z.writestr(name, result[name])
    with zipfile.ZipFile(dest) as z:
        if z.testzip():
            raise ValueError("damaged output ZIP")
    return {
        "stage26_index_sha256": sha(original["index.html"]),
        "stage28_index_sha256": sha(result["index.html"]),
        "stage28_zip_sha256": sha(dest.read_bytes()),
        "removed_staging_files": [OLD_JS, OLD_CSS],
        "added_from_exact_host_archive": {key: sha(restored[key]) for key in MISSING},
        "all_local_asset_references_present": True,
        "staged_file_count": len(result),
        "not_deployed": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage26", type=Path, required=True)
    parser.add_argument("--host-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(make(args.stage26, args.host_archive, args.output), indent=2))


if __name__ == "__main__":
    main()
