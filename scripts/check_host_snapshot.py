"""Offline, read-only check of the supplied cPanel snapshot against known baselines.
Do not commit host archives or private directories to this public repository.
Usage: python scripts/check_host_snapshot.py /path/to/public_html
Exit 1 on drift or missing required file. No network or writes.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {
    "index.html": "66b98ea37de9ff31cd73058b406a14ba6104585f478e1b09f76aeeea3a34861a",
    "online/nwp_upload.php": "4b57c03a5498194efeec5bafc7a4a8e11885da7529563c3232d6f1ed10dcc9f9",
}
# Archived host uploader is newer than the two repository-root candidates.
# A known snapshot is not proof that a live server or its runtime is healthy.
def check(root):
    rows = []
    root = root.resolve(strict=True)
    for name, expected in EXPECTED.items():
        p = root / name
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root):
            rows.append({"path": name, "status": "missing-or-unsafe"})
            continue
        with p.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        rows.append({"path": name, "status": "match" if actual == expected else "drift",
                     "expected_sha256": expected, "actual_sha256": actual})
    return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    rows = check(args.root)
    print(json.dumps(rows, indent=2))
    return int(any(row["status"] != "match" for row in rows))

if __name__ == "__main__":
    raise SystemExit(main())
