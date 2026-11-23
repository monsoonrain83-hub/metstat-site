#!/usr/bin/env python3
"""Build and validate UI P1 against the ACTUAL site_src.zip in this checkout.
Never writes to the archive or deployment paths.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1])
css=root/"site/src/css/app.css"
candidate=Path(__file__).with_name("ui_phase1.css").read_text(encoding="utf-8")
base=css.read_text(encoding="utf-8")
marker="/* MetStat UI foundation P1"
if marker in base:
    print("ERROR: source already contains P1; review manually")
    sys.exit(2)
anchors=["#flMain .flLayL .mtLg input{width:20px;height:20px}"]
if not all(a in base for a in anchors):
    print("ERROR: current site_src.zip does not match r193 CSS anchor; abort")
    sys.exit(3)
for required in ["#onViewer .nvChipRow .wxBar","#onViewer .nvTime",":focus-visible","prefers-reduced-motion"]:
    if required not in candidate:
        print("ERROR: missing candidate selector",required)
        sys.exit(4)
css.write_text(base.rstrip()+"\n\n"+candidate.strip()+"\n",encoding="utf-8")
print("Applied P1 to extracted source only:",css)
