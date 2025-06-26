import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("⚡ Feedback function started")

    try:
        data = req.get_json()
        logging.info(f"📥 Received payload: {data}")
    except Exception as e:
        logging.error(f"❌ Failed to parse JSON: {e}")
        return func.HttpResponse(
            json.dumps({ "error": "Invalid JSON", "details": str(e) }),
            mimetype="application/json",
            status_code=400
        )

    name = data.get("name")
    feedback = data.get("feedback")

    if not name or not feedback:
        logging.warning("⚠️ Missing required fields")
        return func.HttpResponse(
            json.dumps({ "error": "Both name and feedback are required." }),
            mimetype="application/json",
            status_code=400
        )

    try:
        logging.info("💾 Pretending to save to database (simulate)")
        # Simulate success
        return func.HttpResponse(
            json.dumps({
                "status": "ok",
                "code": 200,
                "message": "Feedback submitted"
            }),
            mimetype="application/json",
            status_code=200
)


    except Exception as e:
        logging.exception("🔥 Unexpected server error")
        return func.HttpResponse(
            json.dumps({ "error": "Internal server error", "details": str(e) }),
            mimetype="application/json",
            status_code=500
        )
