import azure.functions as func
import logging
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        file = req.files.get('file') if req.files else None
        if not file:
            logging.warning("No file uploaded")
            return func.HttpResponse(
                json.dumps({
                    "error": "No file uploaded",
                    "has_files": bool(req.files),
                    "headers": dict(req.headers)
                }),
                mimetype="application/json",
                status_code=400
            )

        filename = getattr(file, "filename", "no-name")
        return func.HttpResponse(
            json.dumps({
                "message": f"Received file: {filename}"
            }),
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Function crashed")
        return func.HttpResponse(
            json.dumps({
                "error": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )
