#!/usr/bin/env python3
"""MetStat release auditor: read-only. Does not deploy, modify or delete site files."""
import argparse, gzip, hashlib, json, re, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

class IndexRefs(HTMLParser):
    def __init__(self):
        super().__init__(); self.resources=[];self.inline_js=0;self.style_blocks=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="script":
            if a.get("src"):self.resources.append(("script",a["src"]))
            else:self.inline_js+=1
        if tag=="style":self.style_blocks+=1
        if tag=="link" and "stylesheet" in a.get("rel","").split() and a.get("href"):
            self.resources.append(("stylesheet",a["href"]))

def audit(root,manifest=None,sitemap=None):
    index=(root/"index.html").read_bytes();html=index.decode("utf-8",errors="replace")
    refs=IndexRefs();refs.feed(html);resources=[]
    for kind,url in refs.resources:
        path=urlsplit(url)
        if path.scheme or path.netloc or url.startswith("//"):
            resources.append(dict(kind=kind,url=url,external=True));continue
        file=(root/path.path.lstrip("/")).resolve()
        safe=root==file or root in file.parents
        exists=safe and file.is_file()
        item=dict(kind=kind,url=url,external=False,exists_in_snapshot=bool(exists))
        if exists:
            data=file.read_bytes();item.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        resources.append(item)
    routes=json.loads(manifest.read_text()) if manifest and manifest.exists() else []
    paths={r["path"] for r in routes if "path" in r}
    urls=[e.text for e in ET.parse(sitemap).findall(".//{*}loc")] if sitemap and sitemap.exists() else []
    return {
        "source":"read-only local snapshot; does not verify host",
        "html_bytes":len(index),"html_gzip_bytes":len(gzip.compress(index)),
        "inline_scripts":refs.inline_js,"style_blocks":refs.style_blocks,
        "inline_important_count":html.count("!important"),
        "script_style_resources":resources,
        "routes_in_manifest":len(paths),"sitemap_url_count":len(urls),
        "sitemap_paths_not_in_manifest":[u for u in urls if urlsplit(u).path not in paths|{"/"}],
        "manifest_routes_not_in_sitemap":[p for p in sorted(paths) if p not in {urlsplit(u).path for u in urls}],
        "notice":"Missing files in partial snapshots are not proof of missing production assets. Not all routes are public or indexable; NEVER blindly add every manifest route to sitemap."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--manifest");p.add_argument("--sitemap");p.add_argument("--output",required=True)
    a=p.parse_args();root=Path(a.root).resolve();result=audit(root,Path(a.manifest) if a.manifest else None,Path(a.sitemap) if a.sitemap else None)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Audited",root,"resources:",len(result["script_style_resources"]),"routes:",result["routes_in_manifest"])
