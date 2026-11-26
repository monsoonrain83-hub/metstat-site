"""Check the rainfall API/client version contract in a candidate release.

Read-only check; requires both current lookup PHP and client HTML. For a
partial release, overlay its files onto a verified baseline before checking.
This checks literal protocol declarations, not runtime API behaviour.
"""
import argparse
from pathlib import Path
import re
import sys
import zipfile

API = "online/rain_station_lookup_unified_v61.php"
CLIENT = "online/station_isohyet_unified_v66.html"

def check_contract(api, client):
    versions = set(re.findall(r"'version'\s*=>\s*'([^']+)'", api))
    m = re.search(r"if\s*\(!\s*\[([^\]]+)\]\.includes\(x\.version\)\)", client)
    if m:
        accepted = set(re.findall(r"'([^']+)'", m.group(1)))
    else:
        accepted = set(re.findall(r"x\.version\s*!==\s*'([^']+)'", client))
    issues = []
    if not versions:
        issues.append("no literal API version found")
    if not accepted:
        issues.append("no recognized client version check found")
    if versions - accepted:
        issues.append("unsupported API versions: " + ", ".join(sorted(versions - accepted)))
    if len(versions) != 1:
        issues.append("status and lookup must expose one stable protocol version")
    return issues

def check_release(path):
    if path.is_dir():
        return check_contract((path / API).read_text(encoding="utf-8"),
                              (path / CLIENT).read_text(encoding="utf-8"))
    with zipfile.ZipFile(path) as z:
        texts = []
        for name in (API, CLIENT):
            matches = [n for n in z.namelist() if n == name or n.endswith("/" + name)]
            if len(matches) != 1:
                return ["missing or duplicate release member: " + name]
            texts.append(z.read(matches[0]).decode("utf-8"))
        return check_contract(*texts)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    args = parser.parse_args()
    try:
        issues = check_release(args.release)
    except (OSError, UnicodeError, zipfile.BadZipFile) as e:
        print("Cannot inspect release:", e, file=sys.stderr)
        return 2
    for issue in issues:
        print(issue, file=sys.stderr)
    if not issues:
        print("OK: rainfall version contract (runtime integration tests still required)")
    return int(bool(issues))

if __name__ == "__main__":
    sys.exit(main())
