#!/usr/bin/env python3
"""Read-only forensic inventory for a user-provided MetStat host backup.

Never extracts, executes, uploads or modifies host files. Intended to locate
lost isohyet UI assets and compare their content against a supplied ACTIVE
snapshot before a human-authorized release.
"""
import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

ASSETS = ("station_isohyet_v26.html", "station_match_v39.js")
MAX_ZIP_ENTRIES = 50000
MAX_RELEVANT_BYTES = 16 * 1024 * 1024
MAX_COMPRESSION_RATIO = 250
NAV_TERMS = (r"isohyet", r"همبارش")
SENSITIVE = re.compile(r"(^|/)(admin/private|\.env|config\.json|auth\.php)(/|$)", re.I)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    p = PurePosixPath(name.replace("\\", "/"))
    return not (p.is_absolute() or ".." in p.parts or not p.parts or ":" in p.parts[0])


def inspect_zip(path):
    records = []
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > MAX_ZIP_ENTRIES:
            raise ValueError("Too many archive members")
        seen = set()
        for info in members:
            if info.is_dir():
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Symbolic links are not permitted in host backups")
            canonical = info.filename.replace("\\\\", "/").casefold()
            if canonical in seen:
                raise ValueError("Duplicate archive member path")
            seen.add(canonical)
            if not safe_name(info.filename):
                raise ValueError("Unsafe archive member path")
            # No archive member is extracted; no sensitive bytes are returned.
            basename = PurePosixPath(info.filename).name
            if basename not in ASSETS and basename not in ("index.html", "index_new.html"):
                continue
            if info.file_size > MAX_RELEVANT_BYTES:
                raise ValueError("Oversized relevant member")
            if info.file_size and (info.compress_size == 0 or info.file_size / info.compress_size > MAX_COMPRESSION_RATIO):
                raise ValueError("Suspicious compression ratio for relevant member")
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ValueError("Truncated archive member")
            row = {"path": info.filename, "bytes": len(data), "sha256": sha256(data)}
            if basename.startswith("index"):
                text = data.decode("utf-8", errors="replace")
                row["isohyet_reference_count"] = sum(len(re.findall(term, text, re.I)) for term in NAV_TERMS)
            records.append(row)
    return records


def audit(backup, active_index=None):
    if not zipfile.is_zipfile(backup):
        raise ValueError("Backup must be ZIP; no unpacking supported")
    rows = inspect_zip(backup)
    result = {"backup": str(backup), "entries": rows, "live_verified": False,
              "deploy_allowed": False, "warnings": []}
    if active_index is not None:
        data = Path(active_index).read_bytes()
        result["active_index"] = {"bytes": len(data), "sha256": sha256(data),
            "isohyet_reference_count": sum(len(re.findall(t, data.decode("utf-8", errors="replace"), re.I))
                                           for t in NAV_TERMS)}
        result["warnings"].append("An ACTIVE file alone cannot prove Document Root, auth API or rollback")
    else:
        result["warnings"].append("No verified ACTIVE index supplied; do not patch live index")
    present = {PurePosixPath(r["path"]).name for r in rows}
    for required in ASSETS:
        if required not in present:
            result["warnings"].append("Missing from supplied archive: " + required)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backup", type=Path, required=True)
    p.add_argument("--active-index", type=Path)
    p.add_argument("--out", type=Path, help="Optional local JSON report; never a host path")
    args = p.parse_args()
    report = audit(args.backup, args.active_index)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
