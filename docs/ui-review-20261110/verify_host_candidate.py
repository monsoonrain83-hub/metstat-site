#!/usr/bin/env python3
"""Offline, read-only release gate for MetStat P1 candidate.
Usage: python verify_host_candidate.py CURRENT_INDEX.html ORIGINAL_INDEX.html CANDIDATE_INDEX.html
"""
from pathlib import Path
from hashlib import sha256
import sys
if len(sys.argv)!=4:
    sys.exit("Usage: verify_host_candidate.py CURRENT_INDEX.html ORIGINAL_INDEX.html CANDIDATE_INDEX.html")
current, original, candidate=[Path(p).read_bytes() for p in sys.argv[1:]]
expected="7815a55e1a59b1f2869eff39dd7b07f690b96979a013ac0134026643e1383e28"
actual=sha256(current).hexdigest()
print("current_sha256",actual)
if actual!=expected or original!=current:
    sys.exit("BLOCKED: current host index differs from P1 source backup")
needle=b'<style id="metstat-ui-p1">'
if candidate.count(needle)!=1:sys.exit("BLOCKED: missing/duplicate P1 CSS block")
prefix, rest=candidate.split(needle)
css, tail=rest.split(b'</style>\n',1)
if b'<script' in css.lower() or prefix[:-1]+tail!=original:
    sys.exit("BLOCKED: non-CSS changes detected")
print("PASS: candidate is CSS-only relative to current host index")
print("RELEASE STILL BLOCKED until three-device visual/interaction tests pass")
