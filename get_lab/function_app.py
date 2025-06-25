import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("Request received")
        file = req.files.get('file') if req.files else None

        if not file:
            return func.HttpResponse(
                json.dumps({
                    "error": "No file uploaded",
                    "has_files": bool(req.files),
                    "content_type": req.headers.get("Content-Type", "missing")
                }),
                mimetype="application/json",
                status_code=400
            )

        # Simulate file read
        filename = getattr(file, "filename", "no-name")
        return func.HttpResponse(
            json.dumps({
                "message": f"Received file: {filename}"
            }),
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Exception occurred")
        return func.HttpResponse(
            json.dumps({ "error": str(e) }),
            mimetype="application/json",
            status_code=500
        )
