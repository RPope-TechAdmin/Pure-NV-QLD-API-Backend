import jwt
from jwt import PyJWKClient

def validate_token(token):
    tenant_id = "655e497b-f0e8-44ed-98fb-77680dd02944"
    client_id = "767020ce-1519-45e6-94c8-a3b8620230b3"
    jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"

    jwk_client = PyJWKClient(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience={client_id},
        issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    )

    return decoded  # contains claims
