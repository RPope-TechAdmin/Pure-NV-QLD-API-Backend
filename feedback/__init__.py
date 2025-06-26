import azure.functions as func
import logging
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("📥 Received feedback submission")

        data = req.get_json()
        logging.info(f"📄 Payload: {data}")

        name = data.get("name")
        feedback = data.get("feedback")

        if not name or not feedback:
            return func.HttpResponse(
                json.dumps({ "error": "Missing name or feedback" }),
                mimetype="application/json",
                status_code=400
            )

        # Replace this with your actual processing logic
        logging.info(f"✅ Feedback received from {name}: {feedback}")

        return func.HttpResponse(
            json.dumps({ "message": "Feedback submitted successfully" }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.exception("❌ Unexpected server error")
        return func.HttpResponse(
            json.dumps({ "error": str(e) }),
            mimetype="application/json",
            status_code=500
        )
