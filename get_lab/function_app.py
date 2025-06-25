import logging
import azure.functions as func
import pandas as pd
import io
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    file = req.files.get('file') if req.files else None

    if not file:
        logging.warning("No file was uploaded with the request.")
        return func.HttpResponse(
            json.dumps({"error": "No file uploaded"}),
            mimetype="application/json",
            status_code=400
        )

    # Log the uploaded filename
    filename = getattr(file, "filename", "unknown")
    logging.info(f"Uploaded file: {filename}")

    ext = filename.lower().split('.')[-1]

    # Validate file extension
    if ext not in ('xlsx', 'xls', 'csv'):
        logging.warning("Invalid file type uploaded.")
        return func.HttpResponse(
            json.dumps({"error": "Invalid file type. Please upload a .xlsx, .xls, or .csv file."}),
            mimetype="application/json",
            status_code=400
        )

    try:
        in_memory_file = io.BytesIO(file.read())
        in_memory_file.seek(0)

        if ext == 'csv':
            df = pd.read_csv(in_memory_file)
        else:
            df = pd.read_excel(in_memory_file)

        # Optional filtering
        filtered = df[df['Status'] == 'Active'] if 'Status' in df.columns else df

        return func.HttpResponse(
            filtered.to_json(orient='records'),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.exception("Error processing file")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
