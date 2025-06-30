import logging
import azure.functions as func
import pyodbc
import os
import json
import jwt
import struct
from jwt import PyJWKClient
from azure.identity import ManagedIdentityCredential

def validate_token(token):
    tenant_id = "655e497b-f0e8-44ed-98fb-77680dd02944"
    client_id = "bce610d8-2607-48f3-b6e2-fd9acef2732d"
    jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"

    unverified = jwt.decode(token, options={"verify_signature": False})
    logging.info(f"🪪 Unverified token: {json.dumps(unverified, indent=2)}")

    jwk_client = PyJWKClient(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=f"api://{client_id}",  # or "client_id" if you're using that as audience
        issuer=f"https://sts.windows.net/{tenant_id}/"
    )
    return decoded


def get_db_connection():
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://database.windows.net/").token

    access_token = bytes(token, "utf-8")
    token_struct = struct.pack("=i", len(access_token)) + access_token

    connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=purenvqld.database.windows.net;"
        "Database=Feedback;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Authentication=ActiveDirectoryAccessToken;"
    )

    conn = pyodbc.connect(connection_string, attrs_before={1256: token_struct})
    return conn


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔁 Processing feedback submission")

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

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Narangba.Feedback (Name, Feedback) VALUES (?, ?)", (name, feedback))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.exception("❌ Database error")
        return func.HttpResponse(
            json.dumps({"error": "Server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

    logging.info("✅ Feedback saved to SQL database")
    return func.HttpResponse(
        json.dumps({"code": 200, "message": "Feedback submitted successfully."}),
        status_code=200,
        mimetype="application/json"
    )
