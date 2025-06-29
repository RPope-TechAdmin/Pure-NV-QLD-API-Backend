import logging
import azure.functions as func
import pymssql
import os
import json
import jwt
from jwt import PyJWKClient

def validate_token(token):
    tenant_id = "bce610d8-2607-48f3-b6e2-fd9acef2732d"  # Your tenant ID
    client_id = "655e497b-f0e8-44ed-98fb-77680dd02944"  # Your client/app ID
    jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"

    jwk_client = PyJWKClient(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="api://{client_id}/user_impersonation",  # ← this must match what your app expects
        issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    )

    return decoded

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔁 Processing feedback submission")

    # 🟡 Handle preflight CORS requests (OPTIONS)
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "https://calm-smoke-0485c311e.2.azurestaticapps.net",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
                "Access-Control-Max-Age": "86400"
            }
        )

    # ✅ Log request info
    try:
        raw_body = req.get_body().decode("utf-8")
        logging.info(f"📦 Raw request body: {raw_body}")
    except Exception as e:
        logging.warning(f"Could not decode raw body: {e}")

    logging.info(f"🧾 HTTP Method: {req.method}")
    logging.info(f"📏 Content-Length: {req.headers.get('Content-Length')}")

    # 🔐 Check Authorization header
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return func.HttpResponse(
            json.dumps({"error": "Missing or invalid Authorization header"}),
            status_code=401,
            mimetype="application/json"
        )

    token = auth_header.split(" ")[1]

    try:
        claims = validate_token(token)
    except Exception as e:
        logging.exception("❌ Token validation failed")
        return func.HttpResponse(
            json.dumps({"error": "Unauthorized", "details": str(e)}),
            status_code=401,
            mimetype="application/json"
        )
    
    logging.info(f"Decoded token claims: {json.dumps(claims)}")

    print(jwt.decode(token, options={"verify_signature": False}))

    # 🧾 Parse JSON body
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

    # 🛠️ Connect to Azure SQL
    try:
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

        logging.info("✅ Feedback saved to SQL database")

        return func.HttpResponse(
            json.dumps({"code": 200, "message": "Feedback submitted successfully."}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("❌ Database error")
        return func.HttpResponse(
            json.dumps({"error": "Server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
