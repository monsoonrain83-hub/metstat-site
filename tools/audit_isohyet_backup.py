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


def sha256_file(path):
    """Stream the entire supplied backup for immutable provenance tracking."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    """Reject ambiguous ZIP paths before any archive member is inspected."""
    normalized = name.replace("\\", "/")
    if not normalized or any(ord(ch) < 32 or ord(ch) == 127 for ch in normalized):
        return False
    # PurePosixPath silently collapses empty and dot components. Reject them
    # instead: these aliases can hide duplicate members in different ZIP tools.
    segments = normalized.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        return False
    p = PurePosixPath(normalized)
    return not (p.is_absolute() or ":" in segments[0])


def inspect_zip(path):
    records = []
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > MAX_ZIP_ENTRIES:
            raise ValueError("Too many archive members")
        seen = set()
        files = set()
        directories = set()
        for info in members:
            # Validate directory entries too; an unsafe member must not be silently ignored.
            name_to_validate = info.filename[:-1] if info.is_dir() else info.filename
            if not safe_name(name_to_validate):
                raise ValueError("Unsafe archive member path")
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Symbolic links are not permitted in host backups")
            canonical = PurePosixPath(name_to_validate.replace(chr(92), "/")).as_posix().casefold()
            if canonical in seen:
                raise ValueError("Duplicate archive member path")
            seen.add(canonical)
            if info.is_dir():
                directories.add(canonical)
            else:
                files.add(canonical)
            if info.is_dir():
                continue
            if not safe_name(info.filename):
                raise ValueError("Unsafe archive member path")
            # No archive member is extracted; no sensitive bytes are returned.
            basename = PurePosixPath(info.filename.replace(chr(92), "/")).name
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
        # A ZIP may contain both `online` as a file and `online/asset.js`.
        # Such a tree cannot be restored unambiguously on a filesystem.
        for path in seen:
            parts = path.split("/")
            if any("/".join(parts[:i]) in files for i in range(1, len(parts))):
                raise ValueError("Archive file is an ancestor of another member")
    return records


def audit(backup, active_index=None):
    if not zipfile.is_zipfile(backup):
        raise ValueError("Backup must be ZIP; no unpacking supported")
    rows = inspect_zip(backup)
    result = {"backup": str(backup), "backup_sha256": sha256_file(backup),
              "entries": rows, "live_verified": False,
              "deploy_allowed": False, "warnings": []}
    if active_index is not None:
        data = Path(active_index).read_bytes()
        result["active_index"] = {"bytes": len(data), "sha256": sha256(data),
            "isohyet_reference_count": sum(len(re.findall(t, data.decode("utf-8", errors="replace"), re.I))
                                           for t in NAV_TERMS)}
        result["warnings"].append("An ACTIVE file alone cannot prove Document Root, auth API or rollback")
    else:
        result["warnings"].append("No verified ACTIVE index supplied; do not patch live index")
    # Different folders can contain conflicting versions of the same required asset.
    # Never silently select one as the canonical restored file.
    candidates = {}
    for row in rows:
        name = PurePosixPath(row["path"].replace(chr(92), "/")).name
        if name in ASSETS:
            candidates.setdefault(name, []).append(row)
    for name, matches in candidates.items():
        if len(matches) > 1:
            result["warnings"].append(
                "Ambiguous backup candidates for " + name + ": " + str(len(matches))
                + " copies; verify canonical Document Root and SHA256 manually"
            )
    present = set(candidates)
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
