#!/usr/bin/env python3
"""Read-only SHA-256 gate for MetStat r120 -> r121 cPanel releases.

This script does not upload, delete, modify, or patch anything. A successful
base check means the supplied directory matches the EXACT release base; a
successful release check means ALL listed release files are present and match.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate(root, manifest, phase):
    root = Path(root).resolve()
    manifest = json.loads(Path(manifest).read_text(encoding="utf-8"))
    files = manifest["file_hashes"]
    selected = (
        manifest["changed_upload_files"]
        if phase == "base"
        else manifest["full_release_subset"]
    )
    problems = []
    checks = []
    for name in selected:
        if name not in files:
            problems.append(f"Manifest missing hash entry: {name}")
            continue
        item = files[name]
        relative = Path(name)
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root):
            problems.append(f"Path escapes release root: {name}")
            continue

        expected = item["before_sha256" if phase == "base" else "after_sha256"]
        if expected is None:  # Newly added file must not exist in the base.
            if path.exists():
                problems.append(f"Unexpected pre-existing new file: {name}")
            else:
                checks.append(f"ABSENT {name}")
            continue
        if not path.is_file():
            problems.append(f"Missing: {name}")
            continue
        got = sha256(path)
        if got != expected:
            problems.append(f"SHA256 mismatch: {name} expected={expected} got={got}")
        else:
            checks.append(f"OK {name}")

    version_file = root / "version.json"
    if version_file.is_file():
        try:
            version = json.loads(version_file.read_text(encoding="utf-8"))
            for key, expected in manifest["preserved_contract"].items():
                if version.get(key) != expected:
                    problems.append(f"Preserved contract changed: {key}")
            expected_ui = manifest["ui_build_before" if phase == "base" else "ui_build_after"]
            if version.get("ui_build") != expected_ui:
                problems.append(f"Incorrect ui_build: {version.get('ui_build')} (want {expected_ui})")
        except (ValueError, OSError) as err:
            problems.append(f"Invalid version.json: {err}")
    else:
        problems.append("Missing version.json")

    return checks, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Local cPanel/public_html copy or prepared release dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--phase", required=True, choices=["base", "release"])
    args = parser.parse_args(argv)
    checks, problems = validate(args.root, args.manifest, args.phase)
    for check in checks:
        print(check)
    for problem in problems:
        print("BLOCK:", problem, file=sys.stderr)
    print(f"preflight phase={args.phase} matched={len(checks)} blocked={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
