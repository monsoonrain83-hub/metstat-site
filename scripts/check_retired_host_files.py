"""Read-only release gate for the 15 paths the administrator removed.

Run on a proposed cPanel upload ZIP or unpacked release directory, not on
the entire historical repository. Never modify or delete any input.
"""
import argparse
from pathlib import Path, PurePosixPath
import sys
import zipfile

RETIRED = frozenset("""
metstat_geo_r203_install.php
metstat_r206_install_cli.php
assets/ms_r5_perf_core_ddee74fdbe848c59.js
assets/metstat_r5_stage24_restore_v61_a09a39fe9d79.js
assets/metstat_r5_stage24_restore_v61_adminfix_adc48186e4fb.js
assets/metstat_r5_stage24_restore_v61_manualfix_492ce63bd7d6.js
assets/metstat_r5_stage24_restore.js
assets/metstat_r5_stage23_restore.js
online/api.zip
online/assets.zip
online/rainfall_check_34334a734b9a0cf52c0c73fe.php
online/station_isohyet_unified_v60.html
online/station_isohyet_unified_v61.html
online/station_isohyet_unified_v61_adminfix.html
online/station_isohyet_unified_v61_manualfix.html
""".split())

def check_names(names):
    issues = []
    for raw in names:
        if not isinstance(raw, str) or not raw or '\\' in raw or '\x00' in raw:
            issues.append(f"invalid archive path: {raw!r}")
            continue
        p = PurePosixPath(raw)
        if p.is_absolute() or '..' in p.parts or ':' in raw:
            issues.append(f"unsafe archive path: {raw!r}")
            continue
        parts = p.parts
        # Support public_html/, public html/ or arbitrary ZIP enclosing folder.
        # Suffix comparison also catches renamed enclosing release directories.
        for retired in RETIRED:
            suffix = PurePosixPath(retired).parts
            if tuple(x.casefold() for x in parts[-len(suffix):]) == tuple(x.casefold() for x in suffix):
                issues.append(f"retired deployment file: {raw}")
                break
    return sorted(set(issues))

def check(path):
    if path.is_dir():
        return check_names(x.relative_to(path).as_posix() for x in path.rglob('*') if not x.is_dir())
    with zipfile.ZipFile(path) as archive:
        return check_names(x.filename for x in archive.infolist() if not x.is_dir())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release', type=Path)
    path = parser.parse_args().release
    try:
        issues = check(path)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"Cannot inspect release: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue, file=sys.stderr)
    if not issues:
        print("OK: no retired host files in candidate (not a full security or deployment test)")
    return int(bool(issues))

if __name__ == '__main__':
    sys.exit(main())
