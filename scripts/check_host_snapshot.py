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
# Exact verified frontend packages. Recognition does not imply deployment.
# The uploader pin describes the supplied host snapshot, not a deployment target.
RELEASES = {
    "V87": ("0adaeabb312653692ba463a0bc6c0d24e19a79d9c125ed53aed59eea809ed785",
            "4a4e77930c1b17d3fc39353d32d3c88ac9691edb69d108f84718c1ae49eb239e"),
    "V88": ("52012e1fd5ff0921dbc49823b311b062752dfd3ac17dbbe46503e438587836e6",
            "e8ff91ddd6acd9597556fb17c60e4ffec6d816c3302bfdd3bde2faf455dda040"),
    "V89": ("a27298eb66145a9a8890d21c57330058876b2dd75b0b81604242b62ff9151936",
            "cc3b5fc40594635e03338489bd03fb205de19573938926988d1924f869f92631"),
    "V90": ("22368db76d7c67f4534f8abdf9de5f54eee1160777c56548bba1872c8de58a2c",
            "ee373baac9806769233f4c15a7c72887026e8b766a34f86a5e3af694be31f7a3"),
    "V92": ("054f9d61c2d418b66df078c3550b141416f3b6e9e01262b3b632243239cee770",
            "830b402e8c88464a550e6351e906e729a56650c2c54c4d972546d7cd7c9dc5fa"),
    "V93": ("2bef1bb9201349b41d8202785c8ebff2bb56e03139dbd9cd31de0492df8f5a7d",
            "553f5ac11dfaa0a88ae6eddd8e276b1b2d4952e0f8a0edb61d24a6039acebfab"),
}
RELEASE_ASSETS = {
    "V93": {
        "assets/wb_layer_bold_a44890a39baebfa9.png": "a44890a39baebfa9ff7518ac4434ec69601644baa723fa974dcb0258c9776206",
        "assets/wb_layer_grid_79a8dbfb2bd2d46b.png": "79a8dbfb2bd2d46b62b00d01ffab9792a0e93a74af603f6e073fce8b38426125",
        "assets/wb_layer_orig_cf309ba5758f85d9.png": "cf309ba5758f85d976215373bcfe1be27c64642f85b1e9d0d871b7a49a77ae2c",
    }
}

def release_expected(release):
    html, core = RELEASES[release]
    return {
        "index.html": html,
        f"assets/ms_r5_perf_core_{core[:16]}.js": core,
        "online/nwp_upload.php": EXPECTED["online/nwp_upload.php"],
        **RELEASE_ASSETS.get(release, {}),
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
