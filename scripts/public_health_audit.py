"""Fixed-target, bounded public health audit. Never follows redirects, sends credentials,
reads private URLs, or performs active vulnerability tests. JSON only, no response bodies."""
import hashlib, http.client, ipaddress, json, socket, ssl, time
from html.parser import HTMLParser
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

HOST="wtafkik.ir"
AGENT="MetStat-ReadOnly-Audit/1.0"
HEADERS=("content-type","content-length","content-encoding","cache-control","expires",
         "strict-transport-security","content-security-policy","content-security-policy-report-only",
         "x-frame-options","x-content-type-options","referrer-policy","permissions-policy",
         "access-control-allow-origin","vary")
MAX_HTML=2_000_000
if __package__:
    from .check_host_snapshot import RELEASES
else:
    from check_host_snapshot import RELEASES

def identify_release(digest, core_refs):
    for version,(html,core) in RELEASES.items():
        if digest==html:
            expected="/assets/ms_r5_perf_core_"+core[:16]+".js"
            return {"version":version,"status":"html-match" if core_refs==[expected] else "reference-mismatch","asset_bytes_verified":False}
    return {"version":None,"status":"unknown","asset_bytes_verified":False}
def public_ips(addresses):
    ips=[ipaddress.ip_address(a) for a in addresses]
    if not ips or any(not a.is_global or a.is_multicast or a.is_reserved for a in ips):
        raise ValueError("non-public DNS answer")
    return ips
class PinnedHTTPS(http.client.HTTPSConnection):
    def connect(self):
        addresses=public_ips([r[4][0] for r in socket.getaddrinfo(HOST,443,type=socket.SOCK_STREAM)])
        raw=socket.create_connection((str(addresses[0]),443),timeout=self.timeout)
        try:self.sock=self._context.wrap_socket(raw,server_hostname=HOST)
        except BaseException:raw.close();raise
def request(path,limit):
    if path not in ("/robots.txt","/"):raise ValueError("path outside fixed allowlist")
    c=PinnedHTTPS(HOST,timeout=12,context=ssl.create_default_context())
    start=time.monotonic()
    try:
        c.request("GET",path,headers={"User-Agent":AGENT,"Accept-Encoding":"identity","Connection":"close"})
        r=c.getresponse()
        report={"status":r.status,"ttfb_ms":round((time.monotonic()-start)*1000),"headers":{h:r.getheader(h) for h in HEADERS if r.getheader(h) is not None}}
        # Only retain cookie flags, never values/names or arbitrary headers.
        report["cookie_flags"]=[{k:k in [a.strip().split("=",1)[0].lower() for a in v.split(";")[1:]] for k in ("secure","httponly","samesite")} for v in (r.headers.get_all("Set-Cookie") or [])]
        if r.status!=200:return report,None
        if r.getheader("Content-Encoding","identity").lower()!="identity":report["body"]="unsupported_encoding";return report,None
        b=r.read(limit+1)
        if len(b)>limit:report["body"]="size_limit";return report,None
        report["bytes"]=len(b)
        return report,b
    finally:c.close()
class Resources(HTMLParser):
    def __init__(self):
        super().__init__();self.external=0;self.insecure=0;self.resources=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);url=a.get("src") if tag in ("script","img","iframe") else a.get("href") if tag=="link" else None
        if not url:return
        u=urlsplit(url)
        if u.scheme=="http":self.insecure+=1
        if u.netloc and u.netloc.lower()!=HOST:self.external+=1
        if tag=="script" and not u.netloc and not u.scheme and u.path.startswith("/assets/"):
            self.resources.append(u.path)
def audit():
    result={"target":"https://"+HOST,"scope":"two fixed public GETs maximum; no redirects or crawling","utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    try:
        r,b=request("/robots.txt",65536);result["robots"]=r
        if r["status"]==404:allowed=True
        elif r["status"]==200 and b is not None:
            parser=RobotFileParser();parser.parse(b.decode("utf-8",errors="replace").splitlines());allowed=parser.can_fetch(AGENT,"https://"+HOST+"/")
            # Respect explicit crawl delay; do not sleep for long or ignore it.
            if (parser.crawl_delay(AGENT) or parser.crawl_delay("*") or 0)>2 or parser.request_rate(AGENT) or parser.request_rate("*"):allowed=False
        else:allowed=False
        if not allowed:result["root"]={"status":"skipped_robots"};return result
        time.sleep(2)
        r,b=request("/",MAX_HTML);result["root"]=r
        if b is not None:
            p=Resources();p.feed(b.decode("utf-8",errors="replace"))
            r.update({"sha256":hashlib.sha256(b).hexdigest(),"external_resource_count":p.external,"explicit_http_resources":p.insecure,"local_script_count":len(p.resources),"core_refs":[x for x in p.resources if __import__("re").fullmatch(r"/assets/ms_r5_perf_core_[0-9a-f]{16}\.js",x)]})
            r["release"]=identify_release(r["sha256"],r["core_refs"])
    except (OSError,ValueError,http.client.HTTPException) as e:result["error_type"]=type(e).__name__
    return result
if __name__=="__main__":print(json.dumps(audit(),indent=2))
