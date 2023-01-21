# Get claims in [AWS Cognito](https://aws.amazon.com/cognito/) JWT tokens if they are verified

## Overview
This package can be used to verify jwt tokens to ensure they come from a specific cognito user pool for a specific app client, and that the claims inside it are true.

## Comparison with cognitojwt
This package used the cognitojwt repo as a starting point and much of the code base remains unchanged. The important difference is that in stead of pulling the public keys from cognito with every request, this package caches the Cognito public keys in an environment variable to speed up the verification. If a token's verification fails, the public keys are refreshed from Cognito to cover the edge case where the user pool's keys were updated.

## Performance
- Validation time before public keys are cached (ran test in South Africa and public keys are retreived from us-east-1): 1.0184 s
- Validation time after public keys are cached: 0.0009 s

## Important notes
- tested on Python = 3.9
- if the application is deployed inside a private vpc without internet gateway, the application will not be able to download the JWKS file.
In this case set the 'COGNITO_PUBLIC_KEYS' environment variable to the list of public keys that can be found at 'https://cognito-idp.{region}.amazonaws.com/{userpool_id}/.well-known/jwks.json'. Public keys should not change for the same user pool, but this is up to AWS's discresion, so hardcoding the keys might cause unintended verification failures.

## Installation
pip install git+https://github.com/DanielvNiek/cognitoclaims.git

## Usage
```python
import cognitoclaims

token='ey****'
REGION = '**-****-*'
USERPOOL_ID = 'us-east-1_***'
APP_CLIENT_ID = '3yx****' #can also be a container with multiple ids: APP_CLIENT_ID=('client_one', 'client_two')

try:
    verified_claims: dict = cognitoclaims.get_verified_claims(
        id_token,
        REGION,
        USERPOOL_ID,
        app_client_id=APP_CLIENT_ID,  # Optional
        check_expiration=True  # Disable token expiration check for testing purposes
    )
except Exception as e: # raised if token not verified
    ## handle exception

```
## Running the tests
In order to run the unit tests you will need to add a file called testingCredentials.py in the tests folder and populate the following five methods that should all take 0 arguments and return strings:
- getExpiredAccessToken
- getExpiredIdToken
- getAppClientId
- getTestUserName
- getTestUserPassword


