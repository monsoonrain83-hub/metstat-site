"""Read-only HEAD checks for known log/retired-file paths, deny canaries and public files."""
import json
import sys
import urllib.error
import urllib.request

BASE = "https://wtafkik.ir"
CHECKS = {
    "/admin/private/deny-canary.txt": {403, 404},
    # Files observed in the administrator-provided 25 Nov host archive.
    "/debug.log": {403, 404},
    "/error_log": {403, 404},
    "/admin/error_log": {403, 404},
    "/online/error_log": {403, 404},
    "/online/api.zip": {403, 404},
    "/online/assets.zip": {403, 404},
    "/metstat_data/index.html": {403, 404},
    "/online/data/manifest.json": {200},
    "/": {200},
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def probe(path, allowed):
    req = urllib.request.Request(BASE + path, method="HEAD",
                                 headers={"Cache-Control":"no-cache", "User-Agent":"MetStat-boundary-check/1.0"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=20) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
        e.close()
    except (OSError, ValueError) as e:
        return {"path":path, "status":None, "pass":False, "reason":type(e).__name__}
    return {"path":path, "status":status, "pass":status in allowed}

if __name__ == "__main__":
    rows = [probe(path, allowed) for path, allowed in CHECKS.items()]
    report = {"checks":rows, "scope":"HEAD only; no private body retrieval; 404 does not establish that a file exists or that all private routes are protected"}
    with open("private-boundary-report.json","w",encoding="utf8") as f:
        json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
    sys.exit(0 if all(x["pass"] for x in rows) else 1)
