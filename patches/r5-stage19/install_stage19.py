#!/usr/bin/env python3
"""Non-destructive, repeatable R5 Stage19 asset installer for a *staged* site.

Run `python install_stage19.py /path/to/staged/index.html --dry-run` first.
Never run directly against the cPanel ACTIVE file without backup and rollback.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys

CSS = 'assets/metstat_r5_stage19_controls.css'
JS = 'assets/metstat_r5_stage19_controls.js'
MARK = 'data-ms-stage19="1"'

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def install(index: Path, dry_run: bool) -> str:
    home = Path(__file__).resolve().parent
    text = index.read_text(encoding='utf-8')
    if '</head>' not in text or '</body>' not in text:
        raise ValueError('HTML is missing a head or body closing tag')
    for required in ('id="nvLg"', 'id="nvBm"', 'metstat_map_ui_r201.js'):
        if required not in text:
            raise ValueError(f'Unexpected HTML source; required marker absent: {required}')
    for rel in (CSS, JS):
        if not (home / rel).is_file():
            raise FileNotFoundError(home / rel)
    if MARK in text:
        return 'already-installed (no changes)'
    for rel in (CSS, JS):
        dst = index.parent / rel
        if dst.exists() and sha256(dst) != sha256(home / rel):
            raise FileExistsError(f'Refusing to overwrite differing asset: {dst}')
    text = text.replace('</head>', f'<link rel="stylesheet" href="{CSS}?v=19" {MARK}>\n</head>', 1)
    text = text.replace('</body>', f'<script defer src="{JS}?v=19" {MARK}></script>\n</body>', 1)
    if dry_run:
        return 'dry-run passed (no files written)'
    backup = index.with_suffix(index.suffix + '.stage19.bak')
    if backup.exists():
        raise FileExistsError(f'Backup already exists, preserve it before reinstalling: {backup}')
    shutil.copy2(index, backup)
    for rel in (CSS, JS):
        dest = index.parent / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if (home / rel).resolve() != dest.resolve():
            shutil.copy2(home / rel, dest)
    index.write_text(text, encoding='utf-8')
    return f'installed; rollback index backup={backup}; input SHA256={sha256(backup)}'

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('index', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    try:
        print(install(args.index, args.dry_run))
    except (OSError, ValueError) as e:
        print(f'STOP: {e}', file=sys.stderr)
        raise SystemExit(2)