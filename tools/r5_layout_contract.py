#!/usr/bin/env python3
"""Read-only R5 UI structural and design-token acceptance audit.

Accepts an HTML file or staged ZIP containing index.html; never extracts files,
rewrites a scientific engine, or claims real browser/host verification.
"""
from __future__ import annotations

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from zipfile import BadZipFile, ZipFile

EXPECTED_GEO = ("geoContinent", "geoRegion", "geoCountry", "geoProvince", "geoCounty")
EXPECTED_TOKENS = {
    "--sky": "#399fd4", "--paper": "#f8f9fd", "--scarlet": "#dc1937",
    "--ink": "#183b53", "--muted": "#577489", "--bg": "#eaf4fa",
    "--line": "#c2dfed", "--panel-font": "14px",
}
MAX_INDEX_BYTES = 16 * 1024 * 1024


class Node:
    def __init__(self, name, attrs, parent):
        self.name = name
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)

    def has(self, name):
        return name in (self.attrs.get("class") or "").split()

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()


class DOM(HTMLParser):
    VOID = {"meta", "link", "img", "input", "br", "hr", "source", "area", "base", "embed", "wbr", "col", "track"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("document", [], None)
        self.stack = [self.root]
        self.styles = []

    def handle_starttag(self, name, attrs):
        node = Node(name, attrs, self.stack[-1])
        if name not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, name, attrs):
        Node(name, attrs, self.stack[-1])

    def handle_endtag(self, name):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].name == name:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack[-1].name == "style":
            self.styles.append(data)


def load_source(path: Path) -> bytes:
    if path.suffix.lower() != ".zip":
        if path.stat().st_size > MAX_INDEX_BYTES:
            raise ValueError("HTML exceeds size cap")
        return path.read_bytes()
    with ZipFile(path) as archive:
        names = archive.namelist()
        if names.count("index.html") != 1:
            raise ValueError("ZIP needs one root index.html, no duplicate")
        info = archive.getinfo("index.html")
        if info.file_size > MAX_INDEX_BYTES:
            raise ValueError("index.html exceeds size cap")
        data = archive.read("index.html")  # validates member CRC, no extraction
        if len(data) > MAX_INDEX_BYTES:
            raise ValueError("index.html exceeds size cap")
        return data


def first(nodes, cls):
    return next((n for n in nodes if n.has(cls)), None)


def direct(node, cls):
    return first(node.children, cls) if node else None


def nested(node, cls):
    return first(node.descendants(), cls) if node else None


def analyze(html: bytes) -> dict:
    content = html.decode("utf-8", errors="strict")
    dom = DOM()
    dom.feed(content)
    nodes = list(dom.root.descendants())
    ids = Counter(n.attrs["id"] for n in nodes if n.attrs.get("id"))
    html_node = next((n for n in nodes if n.name == "html"), None)
    app = first(nodes, "app")
    header = direct(app, "header")
    geo = direct(app, "geo-bar")
    workspace = direct(app, "workspace")
    sidebar = direct(workspace, "sidebar")
    content_box = direct(workspace, "content")
    map_card = nested(content_box, "map-card")
    map_stage = nested(map_card, "map-stage")
    header_tools = nested(header, "header-tools")
    geo_ids = [n.attrs.get("id") for n in (geo.descendants() if geo else ()) if n.name == "select"]
    tools_ids = {n.attrs.get("id") for n in (header_tools.descendants() if header_tools else ())}
    styles = "\n".join(dom.styles)
    root_rule = re.search(r":root\s*\{([^{}]*)\}", styles)
    root_css = root_rule.group(1) if root_rule else ""
    token_map = {key: value.strip().lower() for key, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+)", root_css)}
    app_rules = re.findall(r"\.app\s*\{([^{}]*)\}", styles)
    workspace_rules = re.findall(r"\.workspace\s*\{([^{}]*)\}", styles)
    app_has_desktop_width = any(re.search(r"min-width\s*:\s*960px\b", rule) for rule in app_rules)
    workspace_has_sidebar = any(re.search(r"grid-template-columns\s*:\s*328px\s+minmax\(0\s*,\s*1fr\)", rule) for rule in workspace_rules)
    order = [node.has("header") and "header" or node.has("title-strip") and "title-strip" or node.has("geo-bar") and "geo-bar" or node.has("workspace") and "workspace" or "" for node in (app.children if app else ())]
    order = [x for x in order if x]
    checks = {
        "fa_rtl_html": bool(html_node and html_node.attrs.get("lang") == "fa" and html_node.attrs.get("dir") == "rtl"),
        "single_app_mode": len([n for n in nodes if n.has("app")]) == 1 and bool(app and app.attrs.get("data-mode")),
        "r5_region_order": order[:4] == ["header", "title-strip", "geo-bar", "workspace"],
        "sidebar_right_main_left": bool(sidebar and content_box and workspace.children.index(sidebar) < workspace.children.index(content_box)),
        "map_card_stage": bool(map_card and map_stage),
        "five_real_geo_controls": tuple(geo_ids) == EXPECTED_GEO,
        "header_sound_and_font": {"soundBtn", "uiSmaller", "uiBigger"}.issubset(tools_ids),
        "r5_reference_tokens": all(token_map.get(k) == v for k, v in EXPECTED_TOKENS.items()),
        "desktop_canvas_min_960": app_has_desktop_width,
        "right_sidebar_328": workspace_has_sidebar,
        "no_duplicate_dom_ids": all(count == 1 for count in ids.values()),
    }
    failed = [k for k, success in checks.items() if not success]
    return {
        "read_only": True, "passed": not failed, "checks": checks, "failed": failed,
        "observed": {"geo_select_ids": geo_ids, "region_order": order[:6],
                     "duplicate_ids": sorted(k for k, v in ids.items() if v > 1),
                     "tokens": token_map, "dom_nodes": len(nodes),
                     "index_sha256": sha256(html).hexdigest()},
        "limitations": "Static HTML/CSS only: no Playwright, server routes, NWP data, or cPanel deployment checked.",
    }


def main(argv=None) -> int:
    parser = ArgumentParser()
    parser.add_argument("candidate", type=Path, help="HTML file or staged ZIP containing root index.html")
    parser.add_argument("--expected-index-sha256", help="Optional known baseline index checksum")
    args = parser.parse_args(argv)
    try:
        data = load_source(args.candidate)
        report = analyze(data)
        if args.expected_index_sha256 and report["observed"]["index_sha256"] != args.expected_index_sha256.lower():
            report["checks"]["pinned_index_checksum"] = False
            report["failed"].append("pinned_index_checksum")
            report["passed"] = False
    except (OSError, BadZipFile, ValueError, UnicodeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
