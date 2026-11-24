#!/usr/bin/env python3
"""Read-only gate for browser-measured *reference* R5 against administrator's pin.

The golden reference is NOT a production page or cPanel deployment candidate.
A green result does not certify a candidate host's pixel parity or live NWP.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "specs" / "R5_CANONICAL_VISUAL_GOLDEN_20261124.json"


def validate(report: dict, contract: dict) -> dict:
    failures = []
    if report.get("sha256") != contract["source_sha256"]:
        failures.append("wrong_reference_sha")
    actual = report.get("viewports")
    if not isinstance(actual, list) or len(actual) != len(contract["viewports"]):
        return {"passed": False, "failures": failures + ["missing_browser_viewports"]}
    expected = {(v["width"], v["height"]): v for v in contract["viewports"]}
    seen = set()
    for row in actual:
        dims = row.get("viewport")
        if not isinstance(dims, list) or len(dims) != 2 or tuple(dims) not in expected:
            failures.append("unknown_viewport")
            continue
        key = tuple(dims)
        if key in seen:
            failures.append("duplicated_viewport")
        seen.add(key)
        e = expected[key]
        m = row.get("measurements") or {}
        side = m.get("sidebar") or {}
        mp = m.get("map") or {}
        header = m.get("header") or {}
        if m.get("nav") != contract["nav_groups"]:
            failures.append(f"{key}_nav_changed")
        if m.get("models") != contract["model_status_controls"]:
            failures.append(f"{key}_model_control_count_changed")
        if m.get("geographies") != contract["geography"]:
            failures.append(f"{key}_geo_changed")
        if (m.get("lang"), m.get("dir")) != ("fa", "rtl"):
            failures.append(f"{key}_rtl_changed")
        if m.get("tokens") != contract["colors"]:
            failures.append(f"{key}_palette_changed")
        for name, value, target in (
            ("sidebar", side.get("width"), e["sidebar_px"]),
            ("map", mp.get("width"), e["map_px"]),
            ("header", header.get("height"), e["header_px"]),
        ):
            if not isinstance(value, (int, float)) or abs(value - target) > 1:
                failures.append(f"{key}_{name}_width_or_height_changed")
        if m.get("appMinWidth") != str(e["app_min_width_px"]) + "px":
            failures.append(f"{key}_desktop_geometry_changed")
        if not (isinstance(side.get("x"), (int, float)) and isinstance(mp.get("x"), (int, float))
                and mp["x"] < side["x"]):
            failures.append(f"{key}_sidebar_not_to_right_of_map")
        if row.get("page_errors") or not row.get("passed", False):
            failures.append(f"{key}_runtime_error_or_failed_checks")
    if set(expected) != seen:
        failures.append("missing_required_viewport")
    return {"passed": not failures, "failures": sorted(set(failures)),
            "scope": "original R5 offline browser golden only; host and Figma not tested"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("browser_report", type=Path)
    p.add_argument("--contract", type=Path, default=CONTRACT)
    a = p.parse_args()
    try:
        res = validate(json.loads(a.browser_report.read_text(encoding="utf-8")),
                       json.loads(a.contract.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        res = {"passed": False, "failures": [f"invalid_input:{type(exc).__name__}"]}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
