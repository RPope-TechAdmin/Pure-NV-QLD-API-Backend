import logging
import azure.functions as func
import json
import pyodbc
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Method received: {req.method}")

    if req.method != "POST":
        return func.HttpResponse(
            json.dumps({ "error": "Only POST allowed" }),
            mimetype="application/json",
            status_code=405
        )
    
    try:
        data = req.get_json()
        name = data.get("name")
        feedback = data.get("feedback")

        if not name or not feedback:
            return func.HttpResponse(
                json.dumps({ "error": "Missing fields" }),
                mimetype="application/json",
                status_code=400
            )

        # Connect to Azure SQL DB
        conn = pyodbc.connect(
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={os.getenv('SQL_SERVER')};"
            f"Database={os.getenv('SQL_DB')};"
            f"Uid={os.getenv('SQL_USER')};"
            f"Pwd={os.getenv('SQL_PASSWORD')};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        cursor = conn.cursor()

        # Use parameterized query to avoid SQL injection
        cursor.execute(
            "INSERT INTO [Narangba].[Feedback] (Name, Feedback) VALUES (?, ?);",
            (name, feedback)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps({ "message": "Feedback uploaded successfully. Thank you!" }),
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Error submitting feedback")
        return func.HttpResponse(
            json.dumps({ "error": str(e) }),
            mimetype="application/json",
            status_code=500
        )
