"""Fail-closed tests for the administrator's canonical R5 browser golden report."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from tools.r5_uiux_report_gate import CONTRACT, validate


class R5GoldenUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def setUp(self):
        c = self.contract
        self.report = {"sha256": c["source_sha256"], "viewports": []}
        for e in c["viewports"]:
            self.report["viewports"].append({
                "viewport": [e["width"], e["height"]],
                "passed": True, "page_errors": [],
                "measurements": {
                    "nav": c["nav_groups"], "models": c["model_status_controls"],
                    "geographies": c["geography"], "lang": "fa", "dir": "rtl",
                    "tokens": c["colors"],
                    "sidebar": {"x": 700, "width": e["sidebar_px"]},
                    "map": {"x": 0, "width": e["map_px"]},
                    "header": {"height": e["header_px"]},
                    "appMinWidth": str(e["app_min_width_px"]) + "px",
                },
            })

    def check(self):
        return validate(self.report, self.contract)

    def test_complete_matching_four_viewports_pass(self):
        self.assertTrue(self.check()["passed"], self.check())

    def test_ref_hash_pinned(self):
        self.report["sha256"] = "0"*64
        self.assertIn("wrong_reference_sha", self.check()["failures"])

    def test_desktop_sidebar_drift_fails(self):
        self.report["viewports"][0]["measurements"]["sidebar"]["width"] = 280
        self.assertFalse(self.check()["passed"])

    def test_original_model_control_duplication_fails(self):
        self.report["viewports"][2]["measurements"]["models"] += 1
        self.assertFalse(self.check()["passed"])

    def test_remove_one_geographic_select_fails(self):
        self.report["viewports"][1]["measurements"]["geographies"].pop()
        self.assertFalse(self.check()["passed"])

    def test_recolor_brand_fails(self):
        self.report["viewports"][0]["measurements"]["tokens"]["--scarlet"] = "#123456"
        self.assertFalse(self.check()["passed"])

    def test_mobile_single_column_drift_fails(self):
        self.report["viewports"][3]["measurements"]["map"]["x"] = 900
        self.assertFalse(self.check()["passed"])

    def test_browser_error_fails(self):
        self.report["viewports"][3]["page_errors"].append("mock failure")
        self.assertFalse(self.check()["passed"])

    def test_missing_or_duplicate_viewport_fails(self):
        self.report["viewports"][2] = deepcopy(self.report["viewports"][1])
        self.assertFalse(self.check()["passed"])

    def test_missing_viewports_fails(self):
        self.report["viewports"].pop()
        self.assertIn("missing_browser_viewports", self.check()["failures"])

    def test_editor_no_access_is_not_claimed_as_figma_verified(self):
        self.assertIn("not inspected", self.contract["important_decisions"]["figma"])


if __name__ == "__main__":
    unittest.main()
