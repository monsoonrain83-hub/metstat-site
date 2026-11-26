import unittest
from scripts import scan_report as s

def raw(root=None):
    return {"target":s.TARGET,"utc":"2026-11-26T15:32:51Z","root":root or {}}
def rows(r):return {x["id"]:x for x in r["findings"]}
class ReportTests(unittest.TestCase):
    def test_missing_headers_only_when_evidence_available(self):
        r=rows(s.normalize(raw({"status":200,"headers":{"x-frame-options":"SAMEORIGIN"}})))
        self.assertEqual(r["SEC-FRAME"]["status"],"observed")
        self.assertEqual(r["SEC-HSTS"]["status"],"issue")
        self.assertEqual(r["COOKIE-SECURE"]["status"],"unknown")
        self.assertTrue(all(x["status"]=="unknown" for x in s.normalize(raw({"status":503}))["findings"]))
    def test_cookie_flag_and_static_resource_scope(self):
        r=rows(s.normalize(raw({"status":200,"headers":{},"cookie_flags":[{"secure":False,"httponly":True,"samesite":False}],"explicit_http_resources":0,"ttfb_ms":1243})))
        self.assertEqual(r["COOKIE-SECURE"]["status"],"issue")
        self.assertEqual(r["COOKIE-HTTPONLY"]["status"],"observed")
        self.assertIn("identity not retained",r["COOKIE-SECURE"]["evidence"])
        self.assertEqual(r["SEC-STATIC-HTTP"]["status"],"observed")
        self.assertIn("dynamic",r["SEC-STATIC-HTTP"]["evidence"])
    def test_unknown_is_not_resolved(self):
        a=s.normalize(raw({"status":200,"headers":{}}))
        b=s.normalize(raw({"status":503}))
        c={x["id"]:x for x in s.compare(a,b)}
        self.assertEqual(c["SEC-CSP"]["change"],"evidence-lost")
        self.assertEqual({x["id"]:x for x in s.compare(b,a)}["SEC-CSP"]["change"],"new-evidence")
    def test_header_now_observed_not_global_fix(self):
        a=s.normalize(raw({"status":200,"headers":{}}))
        b=s.normalize(raw({"status":200,"headers":{"content-security-policy":"default-src 'self'"}}))
        self.assertEqual({x["id"]:x for x in s.compare(a,b)}["SEC-CSP"]["change"],"issue-not-observed-in-latest")
    def test_html_escaping(self):
        a=raw({"status":200,"headers":{"content-security-policy":"<script>alert(1)</script>"}})
        a["utc"]="<img src=x onerror=alert(1)>"
        out=s.render(s.normalize(a))
        self.assertNotIn("<img src=x",out);self.assertNotIn("<script>",out)
        self.assertIn("&lt;img",out)
    def test_target_and_release(self):
        with self.assertRaises(ValueError):s.normalize({"target":"https://other.example"})
        a=s.normalize(raw({"status":200,"headers":{},"release":{"version":"V93","status":"html-match","asset_bytes_verified":True}}))
        self.assertEqual(a["release_html"],"V93");self.assertFalse(a["asset_bytes_verified"])
    def test_untrusted_fields_not_copied(self):
        a=raw({"status":200,"headers":{"content-security-policy":"PRIVATE_MARKER"},"cookie_flags":[{"secure":"yes","httponly":True,"samesite":True,"value":"PRIVATE_MARKER"}]})
        r=s.normalize(a)
        self.assertNotIn("PRIVATE_MARKER",str(r))
        self.assertEqual(rows(r)["COOKIE-SECURE"]["status"],"unknown")
if __name__=="__main__":unittest.main()
