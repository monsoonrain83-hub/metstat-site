import unittest
from unittest.mock import patch
from scripts import public_health_audit as a
class AuditTests(unittest.TestCase):
    def test_private_dns_rejected(self):
        for addr in ("127.0.0.1","10.0.0.1","169.254.169.254","::1","fc00::1","224.0.0.1"):
            with self.assertRaises(ValueError):a.public_ips(["8.8.8.8",addr])
    def test_fixed_target(self):
        with self.assertRaises(ValueError):a.request("/private",10)
    @patch.object(a,"request")
    def test_disallowed(self,r):
        r.return_value=({"status":200},b"User-agent: *\nDisallow: /")
        self.assertEqual(a.audit()["root"]["status"],"skipped_robots")
        self.assertEqual(r.call_count,1)
    @patch.object(a,"request")
    def test_redirect_not_followed(self,r):
        r.return_value=({"status":302},None)
        self.assertEqual(a.audit()["root"]["status"],"skipped_robots")
        self.assertEqual(r.call_count,1)
    @patch.object(a.time,"sleep")
    @patch.object(a,"request")
    def test_allowed(self,r,sleep):
        r.side_effect=[({"status":404},None),({"status":200},b'<script src="/assets/ms_r5_perf_core_0123456789abcdef.js"></script><img src="http://example.com/x">')]
        root=a.audit()["root"]
        self.assertEqual(root["local_script_count"],1)
        self.assertEqual(root["explicit_http_resources"],1)
        self.assertEqual(len(root["core_refs"]),1)
        self.assertEqual(r.call_count,2)
    @patch.object(a,"request")
    def test_long_delay(self,r):
        r.return_value=({"status":200},b"User-agent: *\nCrawl-delay: 10")
        self.assertEqual(a.audit()["root"]["status"],"skipped_robots")
        self.assertEqual(r.call_count,1)
if __name__=="__main__":unittest.main()
