import os
from typing import Dict, Optional, Union, Container
import requests
import json

from jose import jwk
from jose.utils import base64url_decode

from .constants import PUBLIC_KEYS_URL_TEMPLATE
from .exceptions import CognitoJWTException
from .token_utils import get_unverified_claims, get_unverified_headers, check_expired, check_client_id

def getPublicKeyForToken(publicKeys:list,token:str):
    headers = get_unverified_headers(token)
    kid = headers['kid']
    key = list(filter(lambda k: k['kid'] == kid, publicKeys))
    if not key:
        raise CognitoJWTException('Public key not found in jwks.json')
    else:
        key = key[0]
    return jwk.construct(key)

def getPublicKeysFromOsEnviron():
    keys=os.environ.get('COGNITO_PUBLIC_KEYS')
    if keys==None:
        raise Exception('No public keys in environ')
    keys=json.loads(keys)['keys']
    return keys

def refreshOsEnvironPublicKeysFromCognito(region: str, userpool_id: str):
    keys_url: str = PUBLIC_KEYS_URL_TEMPLATE.format(region, userpool_id)
    r = requests.get(keys_url)
    keys_response = r.json()
    os.environ['COGNITO_PUBLIC_KEYS']=json.dumps(keys_response)

def verifyKey(token):
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    public_keys = getPublicKeysFromOsEnviron()
    pub_key=getPublicKeyForToken(public_keys,token)
    if not pub_key.verify(message.encode('utf-8'), decoded_signature):
        raise CognitoJWTException('Signature verification failed')

def getVerifiedClaims(
        token: str,
        region: str,
        userPoolId: str,
        appClientId: Optional[Union[str, Container[str]]] = None,
        checkIfTokenExpired: bool = True
) -> Dict:
    try:
        verifyKey(token)
    except:
        refreshOsEnvironPublicKeysFromCognito(region,userPoolId)
        verifyKey(token)

    claims = get_unverified_claims(token)
    if checkIfTokenExpired:
        check_expired(claims['exp'])

    if appClientId:
        check_client_id(claims, appClientId)

    return claims
