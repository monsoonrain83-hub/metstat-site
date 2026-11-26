"""Offline, read-only check of the supplied cPanel snapshot against known baselines.
Do not commit host archives or private directories to this public repository.
Usage: python scripts/check_host_snapshot.py /path/to/public_html --release V87
Explicit release selection is required to distinguish a known rollback from the intended deployment.
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
# Exact approved/candidate frontend pairs. V89 is intentionally excluded until approved.
# The uploader pin describes the supplied host snapshot, not a deployment target.
RELEASES = {
    "V87": ("0adaeabb312653692ba463a0bc6c0d24e19a79d9c125ed53aed59eea809ed785",
            "4a4e77930c1b17d3fc39353d32d3c88ac9691edb69d108f84718c1ae49eb239e"),
    "V88": ("52012e1fd5ff0921dbc49823b311b062752dfd3ac17dbbe46503e438587836e6",
            "e8ff91ddd6acd9597556fb17c60e4ffec6d816c3302bfdd3bde2faf455dda040"),
}

def release_expected(release):
    html, core = RELEASES[release]
    return {
        "index.html": html,
        f"assets/ms_r5_perf_core_{core[:16]}.js": core,
        "online/nwp_upload.php": EXPECTED["online/nwp_upload.php"],
    }

# Archived host uploader is newer than the two repository-root candidates.
# A known snapshot is not proof that a live server or its runtime is healthy.
def check(root, expected_files=None):
    rows = []
    root = root.resolve(strict=True)
    for name, expected in (EXPECTED if expected_files is None else expected_files).items():
        p = root / name
        if (not p.is_file() or any(q.is_symlink() for q in (p, *p.parents) if q != root and q.is_relative_to(root))
                or not p.resolve().is_relative_to(root)):
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
    parser.add_argument("--release", choices=sorted(RELEASES), required=True,
                        help="Intended frontend version; never infer from old version.json")
    args = parser.parse_args()
    rows = check(args.root, release_expected(args.release))
    print(json.dumps(rows, indent=2))
    return int(any(row["status"] != "match" for row in rows))

if __name__ == "__main__":
    raise SystemExit(main())
