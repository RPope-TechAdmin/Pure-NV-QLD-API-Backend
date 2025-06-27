import logging
import azure.functions as func
import pymssql
import os
import json
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

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing feedback submission")

    try:
        # Parse JSON body
        try:
            data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON"}),
                status_code=400,
                mimetype="application/json"
            )

        name = data.get("name")
        feedback = data.get("feedback")

        if not name or not feedback:
            return func.HttpResponse(
                json.dumps({"error": "Both 'name' and 'feedback' are required."}),
                status_code=400,
                mimetype="application/json"
            )

        # ✅ Optional: Extract authenticated user info
        user_claims = req.headers.get("x-ms-client-principal")
        if user_claims:
            import base64
            import json
            decoded = base64.b64decode(user_claims).decode("utf-8")
            claims = json.loads(decoded)
            user_email = claims.get("userDetails", "unknown")
        else:
            user_email = "anonymous"

        # ✅ Connect to Azure SQL
        conn = pymssql.connect(
            server=os.environ["SQL_SERVER"],
            user=os.environ["SQL_USER"],
            password=os.environ["SQL_PASSWORD"],
            database=os.environ["SQL_DB"]
        )

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Narangba.Feedback (Name, Feedback) VALUES (%s, %s)",
            (name, feedback)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps({"code": 200, "message": "Feedback submitted successfully."}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Unhandled error")
        return func.HttpResponse(
            json.dumps({"error": "Server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
