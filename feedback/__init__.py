import azure.functions as func
import logging
import json
import pymssql  # or pyodbc depending on your driver
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔍 Feedback function triggered")

    try:
        data = req.get_json()
        logging.info(f"📦 Request JSON: {data}")
    except Exception as e:
        logging.exception("❌ Failed to parse JSON")
        return func.HttpResponse(
            json.dumps({ "error": "Invalid JSON", "details": str(e) }),
            mimetype="application/json",
            status_code=400
        )

    name = data.get("name")
    feedback = data.get("feedback")

    if not name or not feedback:
        logging.warning("⚠️ Missing fields")
        return func.HttpResponse(
            json.dumps({ "error": "Both name and feedback are required." }),
            mimetype="application/json",
            status_code=400
        )

    try:
        logging.info("🔑 Getting DB credentials")
        server = os.getenv("SQL_SERVER")
        user = os.getenv("SQL_USER")
        password = os.getenv("SQL_PASSWORD")
        database = os.getenv("SQL_DB")

        if not all([server, user, password, database]):
            raise Exception("One or more DB environment variables are missing.")

        logging.info(f"🔌 Connecting to {server}/{database} as {user}")
        conn = pymssql.connect(server, user, password, database)
        cursor = conn.cursor()

        logging.info("📤 Inserting into database")
        cursor.execute("INSERT INTO Feedback (name, feedback) VALUES (%s, %s)", (name, feedback))
        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps({ "message": "Feedback saved successfully." }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.exception("❌ DB operation failed")
        return func.HttpResponse(
            json.dumps({ "error": str(e) }),
            mimetype="application/json",
            status_code=500
        )
