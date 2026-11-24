"""Guard R5 route repair against historical duplicate/placeholder regression.

Synthetic test contains no forecast values or host credentials; live-host
acceptance is separately run in browser with the uploaded real index/assets.
"""
from hashlib import sha256
import re
import unittest

from tools.r5_native_applied_router import CHANGES, SOURCE, TARGET, build, digest, scripts


def baseline():
    fragments=[]
    for i in range(19):
        if i==11:
            body=CHANGES[0][0] + "; " + CHANGES[1][0]
        elif i==14:
            body="const mapped=new Set([" + CHANGES[2][0] + "]);"
        else:
            body=f"const owner_{i}={i};"
        fragments.append("<script>"+body+"</script>")
    return ("<!doctype html><html><head><style>.r5{display:grid}</style></head>"
            "<body><div id=\"apApp\"></div>"+"".join(fragments)+"</body></html>").encode()


class NativeOwnerRegression(unittest.TestCase):
    def setUp(self):
        self.original=baseline()
        self.source_hash=digest(self.original)

    def patch(self, original=None, target=None):
        return build(self.original if original is None else original,
                     source_sha=self.source_hash, target_sha=target)

    def test_production_sha_contract(self):
        self.assertEqual(SOURCE,'7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295')
        self.assertEqual(TARGET,'51df572c1cb0a044a803933a31d2d76f355e6cd5912f4ddf955abb468834dec6')

    def test_only_original_two_router_owners_change(self):
        result=self.patch()
        first=scripts(self.original.decode()); second=scripts(result.decode())
        self.assertEqual([i for i,(a,b) in enumerate(zip(first,second)) if a!=b],[11,14])
        for _,replacement in CHANGES:
            self.assertIn(replacement,result.decode())
        self.assertEqual(result.count(b'id="apApp"'),1)
        self.assertEqual(self.original.count(b'!important'),result.count(b'!important'))

    def test_unknown_active_host_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,"changed"):
            self.patch(self.original+b"new hourly build")

    def test_refuse_second_application(self):
        with self.assertRaises(ValueError):
            self.patch(self.patch())

    def test_missing_native_engine_owner_fails(self):
        invalid=self.original.replace(CHANGES[1][0].encode(),b"/* removed */")
        with self.assertRaises(ValueError):
            build(invalid,source_sha=digest(invalid),target_sha=None)

    def test_duplicate_native_owner_fails(self):
        invalid=self.original.replace(CHANGES[1][0].encode(),(CHANGES[1][0]*2).encode())
        with self.assertRaises(ValueError):
            build(invalid,source_sha=digest(invalid),target_sha=None)

    def test_wrong_output_hash_rejected(self):
        with self.assertRaisesRegex(ValueError,"checksum"):
            self.patch(target="f"*64)

    def test_missing_native_r5_router_fails(self):
        invalid=self.original.replace(CHANGES[2][0].encode(),b"'ap','syn'")
        with self.assertRaises(ValueError):
            build(invalid,source_sha=digest(invalid),target_sha=None)


if __name__=='__main__':
    unittest.main()
