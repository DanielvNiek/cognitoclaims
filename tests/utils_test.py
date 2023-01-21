import os
import time
import unittest
from cognitoclaims import token_utils, CognitoJWTException
from testingCredentials import getExpiredTestAccessToken,getExpiredTestIdToken,getAppClientId

class TestUtil(unittest.TestCase):
    def test_get_headers(self):
        headers_id = token_utils.get_unverified_headers(getExpiredTestIdToken())
        headers_access = token_utils.get_unverified_headers(getExpiredTestAccessToken())
        for h in [headers_access,headers_id]:
            self.assertEqual(type(h),dict)
            self.assertIn('kid',h)
            self.assertIn('alg',h) 

    def test_get_claims(self):
        claims_id = token_utils.get_unverified_claims(getExpiredTestIdToken())
        assert isinstance(claims_id, dict)
        assert 'sub' in claims_id.keys()
        assert 'aud' in claims_id.keys()
        assert 'exp' in claims_id.keys()
        claims_access = token_utils.get_unverified_claims(getExpiredTestAccessToken())
        assert isinstance(claims_access, dict)
        assert 'sub' in claims_access.keys()
        assert 'client_id' in claims_access.keys()
        assert 'exp' in claims_access.keys()

    def test_check_expired(self):
        exp = int(time.time()) + 100
        token_utils.check_expired(exp)
        exp = int(time.time()) - 100
        with self.assertRaises(Exception) as context:
            token_utils.check_expired(exp)
        token_utils.check_expired(exp)

    def test_check_client_id(self):
        claims = token_utils.get_unverified_claims(getExpiredTestAccessToken())
        token_utils.check_client_id(claims, getAppClientId())
        token_utils.check_client_id(claims, ['1001001', getAppClientId()])
        with self.assertRaises(Exception):
            token_utils.check_client_id(claims, '1001001')
        with self.assertRaises(Exception):
            token_utils.check_client_id(claims, f'100{getAppClientId()}001')
