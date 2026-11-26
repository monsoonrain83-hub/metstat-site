"""Normalize bounded public audit evidence into safe, comparable reports.
No network, arbitrary commands, user data, or deployment. Only fixed MetStat target.
"""
import argparse
import html
import json
from pathlib import Path

TARGET="https://wtafkik.ir"
MAX_INPUT=262144
# ID, title, priority when observed, header, effect, remediation, effort
RULES=(
    ("SEC-HSTS","HSTS","medium","strict-transport-security","HTTPS downgrade protection not observed","Validate HTTPS for all intended hosts; introduce HSTS with a conservative max-age.","small"),
    ("SEC-CSP","CSP","medium","content-security-policy","Browser script/resource policy not observed","Inventory real script origins and inline dependencies; test report-only first.","large"),
    ("SEC-FRAME","Frame policy","medium","x-frame-options","Clickjacking defense not observed in this header","Verify CSP frame-ancestors or set SAMEORIGIN if compatible.","small"),
    ("SEC-NOSNIFF","MIME sniffing","low","x-content-type-options","MIME sniffing protection not observed","Verify content types; use nosniff.","small"),
    ("SEC-REFERRER","Referrer policy","low","referrer-policy","Explicit referrer privacy policy not observed","Choose a compatible referrer policy.","small"),
    ("SEC-PERMISSIONS","Permissions policy","low","permissions-policy","Explicit feature policy not observed","Inventory browser features; restrict unused features.","medium"),
)
COOKIE_RULES=(
    ("COOKIE-SECURE","Cookie Secure flag","secure","medium","One or more observed cookies lack Secure; identity is unknown.","Identify cookie owner and HTTPS/proxy settings before changing."),
    ("COOKIE-HTTPONLY","Cookie HttpOnly flag","httponly","medium","One or more observed cookies lack HttpOnly; identity is unknown.","Check whether each cookie is intentionally script-readable."),
    ("COOKIE-SAMESITE","Cookie SameSite flag","samesite","medium","One or more observed cookies lack explicit SameSite; identity is unknown.","Check cross-site login flows and set an appropriate SameSite policy."),
)
def finding(id,title,severity,status,evidence,impact,fix,effort):
    return dict(id=id,title=title,severity=severity,status=status,evidence=evidence,impact=impact,remediation=fix,effort=effort)

def normalize(raw):
    if not isinstance(raw,dict) or raw.get("target")!=TARGET:
        raise ValueError("unexpected audit target")
    root=raw.get("root")
    root=root if isinstance(root,dict) else {}
    headers=root.get("headers")
    available=root.get("status")==200 and isinstance(headers,dict)
    rows=[]
    for id,title,severity,key,impact,fix,effort in RULES:
        observed=available and isinstance(headers.get(key),str) and bool(headers[key].strip())
        # Presence alone is not proof that a header's policy is effective.
        status="observed" if observed else "issue" if available else "unknown"
        evidence="Header present; policy not validated." if observed else "Header absent from root response." if available else "Root header evidence unavailable."
        rows.append(finding(id,title,severity,status,evidence,impact,fix,effort))
    cookies=root.get("cookie_flags")
    for id,title,key,sev,impact,fix in COOKIE_RULES:
        valid=available and isinstance(cookies,list) and 0<len(cookies)<=100 and all(isinstance(c,dict) and type(c.get(key)) is bool for c in cookies)
        missing=sum(not c[key] for c in cookies) if valid else 0
        status="issue" if valid and missing else "observed" if valid else "unknown"
        ev=f"{missing} of {len(cookies)} observed cookies without flag; cookie identity not retained." if valid else "No attributable flag evidence."
        rows.append(finding(id,title,sev,status,ev,impact,fix,"medium"))
    mixed=root.get("explicit_http_resources")
    valid=available and type(mixed) is int and mixed>=0
    rows.append(finding("SEC-STATIC-HTTP","Explicit HTTP resource tags","medium","issue" if valid and mixed else "observed" if valid else "unknown",
        f"{mixed} explicit HTTP resource tags in root HTML; dynamic resources not examined." if valid else "Root resource evidence unavailable.",
        "Possible mixed content.","Check dynamic requests and replace insecure URLs.","medium"))
    ttfb=root.get("ttfb_ms")
    valid=available and type(ttfb) is int and 0<=ttfb<=600000
    rows.append(finding("PERF-TTFB","Root TTFB","info","observed" if valid else "unknown",
        f"{ttfb} ms in one request; not field performance." if valid else "Timing unavailable.",
        "Server/network latency affects initial load.","Compare repeated, controlled measurements before tuning.","medium"))
    rel=root.get("release")
    release=None
    if available and isinstance(rel,dict) and rel.get("status")=="html-match" and rel.get("version") in {"V87","V88","V89","V90","V92","V93"}:
        release=rel["version"]
    return {"schema":1,"target":TARGET,"source":"bounded public root audit","utc":str(raw.get("utc",""))[:40],
            "release_html":release,"asset_bytes_verified":False,"findings":rows,
            "limitations":["One public root response; not a full penetration test.","Header presence is not effective-policy verification.","No cookies identified, no private endpoints, no asset hash verification."]}

def compare(previous,current):
    if previous.get("target")!=TARGET or current.get("target")!=TARGET or previous.get("schema")!=1 or current.get("schema")!=1:
        raise ValueError("incompatible reports")
    old={r["id"]:r for r in previous["findings"]}
    changes=[]
    for r in current["findings"]:
        before=old.get(r["id"],{}).get("status","unknown")
        after=r["status"]
        if before==after: state="unchanged"
        elif after=="unknown": state="evidence-lost"
        elif before=="unknown": state="new-evidence"
        elif before=="issue" and after=="observed": state="issue-not-observed-in-latest"
        elif before=="observed" and after=="issue": state="issue-observed-in-latest"
        else: state="changed"
        changes.append({"id":r["id"],"before":before,"after":after,"change":state})
    return changes

def render(report):
    esc=lambda x:html.escape(str(x),quote=True)
    columns=("id","title","severity","status","evidence","impact","remediation","effort")
    rows="".join("<tr>"+"".join("<td>"+esc(r[k])+"</td>" for k in columns)+"</tr>" for r in report["findings"])
    diff="".join("<tr>"+"".join("<td>"+esc(r[k])+"</td>" for k in ("id","before","after","change"))+"</tr>" for r in report.get("comparison",[]))
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MetStat audit</title><style>body{font:15px system-ui;margin:24px;color:#172b3a}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #ccd4dd;padding:9px;text-align:left;vertical-align:top}th{background:#eef2f6}h1{font-size:24px}</style><h1>MetStat public audit</h1><p>'+esc(report["target"])+' | '+esc(report["utc"])+' | HTML release: '+esc(report["release_html"] or "unknown")+'</p><p>Asset bytes not verified. Presence is not a policy validation.</p><table><thead><tr>'+"".join("<th>"+esc(k)+"</th>" for k in columns)+'</tr></thead><tbody>'+rows+'</tbody></table><h2>Comparison</h2><table><tr><th>ID</th><th>Before</th><th>After</th><th>Change</th></tr>'+diff+'</table><p>'+esc(" ".join(report["limitations"]))+'</p></html>'

def load(path):
    with Path(path).open("rb") as f: data=f.read(MAX_INPUT+1)
    if len(data)>MAX_INPUT: raise ValueError("report too large")
    return json.loads(data)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("current",type=Path)
    p.add_argument("--previous",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    r=normalize(load(args.current))
    if args.previous:r["comparison"]=compare(normalize(load(args.previous)),r)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"findings.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
    (args.output/"findings.html").write_text(render(r),encoding="utf-8")
if __name__=="__main__":main()
