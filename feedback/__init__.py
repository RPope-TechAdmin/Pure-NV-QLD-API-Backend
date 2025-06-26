import azure.functions as func
import pymssql
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        name = data.get("name")
        feedback = data.get("feedback")

        if not name or not feedback:
            return func.HttpResponse(
                json.dumps({ "error": "Missing name or feedback" }),
                mimetype="application/json",
                status_code=400
            )

        # Connect to Azure SQL with pymssql
        conn = pymssql.connect(
            server=os.getenv("SQL_SERVER"),
            user=os.getenv("SQL_USER"),
            password=os.getenv("SQL_PASSWORD"),
            database=os.getenv("SQL_DB")
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Feedback (name, feedback) VALUES (%s, %s)", (name, feedback))
        conn.commit()
        conn.close()

        return func.HttpResponse(
            json.dumps({ "message": "Feedback submitted successfully" }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({ "error": str(e) }),
            mimetype="application/json",
            status_code=500
        )
