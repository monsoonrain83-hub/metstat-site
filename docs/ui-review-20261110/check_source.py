#!/usr/bin/env python3
"""Static source checks for MetStat UI P1. Run against unpacked reconstructed site."""
from pathlib import Path
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path("site")
css=(root/"src/css/app.css").read_text(encoding="utf-8")
online=(root/"src/js/34_online.js").read_text(encoding="utf-8")
rows=(root/"src/js/82_nv_rows.js").read_text(encoding="utf-8")
checks={
 "P1 CSS marker": "MetStat UI foundation P1" in css,
 "mobile chip scroll": "#onViewer .nvChipRow .wxBar" in css and "overflow-x:auto" in css,
 "visible keyboard focus": ":focus-visible" in css,
 "reduced motion": "prefers-reduced-motion" in css,
 "map generated from manifest": "vw.innerHTML=has?nvViewerHTML()" in online,
 "controls mirrored (not deleted)": "data-mir" in rows and "wxSet" in rows,
 "desktop sidebar threshold": "window.innerWidth>=1000" in rows,
 "desktop phone special mode preserved": 'classList.contains("nvfOn")' in rows,
}
for k,v in checks.items(): print(("PASS" if v else "FAIL")+" "+k)
sys.exit(0 if all(checks.values()) else 1)
