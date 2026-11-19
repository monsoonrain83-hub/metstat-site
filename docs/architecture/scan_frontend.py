#!/usr/bin/env python3
"""Read-only MetStat frontend source scanner. No network requests or host writes."""
import argparse
import hashlib
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit


class SourceRefs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.css = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        elif tag == "link" and "stylesheet" in a.get("rel", "").split() and a.get("href"):
            self.css.append(a["href"])


def main():
    p = argparse.ArgumentParser(description="Inspect a local MetStat site source snapshot")
    p.add_argument("--root", required=True, help="Directory containing index.html")
    p.add_argument("--output", required=True, help="JSON inventory output path")
    args = p.parse_args()
    root = Path(args.root).resolve()
    index = root / "index.html"
    if not index.is_file():
        p.error("index.html not found at supplied root")
    parser = SourceRefs()
    parser.feed(index.read_text(encoding="utf-8", errors="replace"))

    def inspect(ref):
        url = urlsplit(ref)
        if url.scheme or url.netloc or ref.startswith("//"):
            return {"ref": ref, "scope": "external", "present": None}
        local = (root / url.path.lstrip("/")).resolve()
        if root not in local.parents and local != root:
            return {"ref": ref, "scope": "out-of-root", "present": False}
        if not local.is_file():
            return {"ref": ref, "scope": "local", "present": False}
        data = local.read_bytes()
        return {"ref": ref, "scope": "local", "present": True,
                "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    report = {
        "root": str(root), "source": "read-only local snapshot",
        "index_sha256": hashlib.sha256(index.read_bytes()).hexdigest(),
        "script_references": [inspect(x) for x in parser.scripts],
        "stylesheet_references": [inspect(x) for x in parser.css],
        "warning": "Changed-only release packages omit most assets. Missing files in a partial snapshot are not proof of missing production assets."
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Scanned {len(parser.scripts)} JS + {len(parser.css)} CSS references; wrote {output}")


if __name__ == "__main__":
    main()
