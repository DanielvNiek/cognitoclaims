import cognitoclaims
from testingCredentials import getAppClientId,getUserPoolId,getUserPoolRegion,getTestUserName,getTestUserPassword,getExpiredTestAccessToken,getExpiredTestIdToken,getExpectedPublicKeys
import unittest
import boto3
import json,os,time

def getAccessTokenForTestUser():
    provider_client=boto3.client('cognito-idp', region_name=getUserPoolRegion())
    auth_data = { 'USERNAME':getTestUserName() , 'PASSWORD':getTestUserPassword()}
    resp = provider_client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH', AuthParameters=auth_data, ClientId=getAppClientId())
    return resp['AuthenticationResult']['AccessToken']

class TestClaims(unittest.TestCase):
    def test_decode_id_token_with_app_id(self):
        claims = cognitoclaims.getVerifiedClaims(
            getExpiredTestIdToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
            checkIfTokenExpired=False
        )
        self.assertIsInstance(claims, dict)

    def test_decode_id_token_without_app_id(self):
        claims = cognitoclaims.getVerifiedClaims(
            getExpiredTestIdToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            checkIfTokenExpired=False
        )
        self.assertIsInstance(claims, dict)

    def test_decode_access_token_with_app_id(self):
        claims = cognitoclaims.getVerifiedClaims(
            getExpiredTestAccessToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
            checkIfTokenExpired=False
        )
        self.assertIsInstance(claims, dict)

    def test_decode_access_token_without_app_id(self):
        claims = cognitoclaims.getVerifiedClaims(
            getExpiredTestAccessToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            checkIfTokenExpired=False
        )
        self.assertIsInstance(claims, dict)

    def test_expiredAccessToken(self):
        with self.assertRaises(Exception) as context:
            cognitoclaims.getVerifiedClaims(
                getExpiredTestAccessToken(),
                getUserPoolRegion(),
                getUserPoolId(),
                getAppClientId(),
            )
        self.assertEqual(str(context.exception),'Token is expired')

    def test_nonExpiredAccessToken(self):
        claims = cognitoclaims.getVerifiedClaims(
            getAccessTokenForTestUser(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
        )
        self.assertIsInstance(claims, dict)

    def test_environmentVariableUsedAfterFirstVerification(self):
        t1=time.time()
        cognitoclaims.getVerifiedClaims(
            getExpiredTestAccessToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
            checkIfTokenExpired=False
        )
        t2=time.time()
        self.assertEqual(json.loads(os.environ.get('COGNITO_PUBLIC_KEYS')),getExpectedPublicKeys()) # type: ignore
        t3=time.time()
        cognitoclaims.getVerifiedClaims(
            getExpiredTestAccessToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
            checkIfTokenExpired=False
        )
        t4=time.time()
        print(t2-t1)
        print(t4-t3)
        self.assertGreater(t2-t1,2*(t4-t3))

    def test_publicKeysAreRefreshedIfInvalid(self):
        t1=time.time()
        cognitoclaims.getVerifiedClaims(
            getExpiredTestAccessToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
            checkIfTokenExpired=False
        )
        pubKeys=getExpectedPublicKeys()
        for key in pubKeys['keys']:
            key['kid']='asdf'
        os.environ['COGNITO_PUBLIC_KEYS']=json.dumps(pubKeys)
        claims=cognitoclaims.getVerifiedClaims(
            getExpiredTestAccessToken(),
            getUserPoolRegion(),
            getUserPoolId(),
            getAppClientId(),
            checkIfTokenExpired=False
        )
        self.assertIsInstance(claims, dict)