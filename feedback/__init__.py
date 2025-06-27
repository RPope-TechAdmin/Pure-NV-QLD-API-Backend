import azure.functions as func
import pymssql
import os
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔁 Feedback function triggered")

    try:
        content_type = req.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            raise ValueError("Missing or incorrect Content-Type header. Expected 'application/json'.")

        data = req.get_json()
        logging.info(f"📦 Received data: {data}")
    except Exception as e:
        logging.exception("❌ Failed to parse JSON body or invalid headers")
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid JSON or headers",
                "details": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

    name = data.get("name")
    feedback = data.get("feedback")

    if not name or not feedback:
        logging.warning("⚠️ Missing required fields")
        return func.HttpResponse(
            json.dumps({ "error": "Both 'name' and 'feedback' fields are required." }),
            mimetype="application/json",
            status_code=400
        )

    try:
        server = os.getenv("SQL_SERVER")
        user = os.getenv("SQL_USER")
        password = os.getenv("SQL_PASSWORD")
        database = os.getenv("SQL_DB")

        if not all([server, user, password, database]):
            raise ValueError("One or more required DB environment variables are missing.")

        logging.info("🔌 Connecting to Azure SQL with Server={server}, Database={database}, Login={user} and Password={password}")
        conn = pymssql.connect(server='purenvqld.database.windows.net', user='rpope@purenv.au', password='Red-R0ck6341', database='Feedback')
        cursor = conn.cursor()

        logging.info("📤 Executing Query: INSERT INTO Narangba.Feedback (Name, Feedback) VALUES ({name}, {feedback});")
        cursor.execute("INSERT INTO Feedback (name, feedback) VALUES (%s, %s)", (name, feedback))
        conn.commit()
        conn.close()

        logging.info("✅ Feedback saved successfully")
        return func.HttpResponse(
            json.dumps({ "message": "Feedback submitted successfully" }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.exception("🔥 Unhandled server error")
        return func.HttpResponse(
            json.dumps({ "error": "Internal Server Error", "details": str(e) }),
            mimetype="application/json",
            status_code=500
        )
