import logging
import azure.functions as func
import pandas as pd
import io
import json
from requests_toolbelt.multipart import decoder

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        content_type = req.headers.get('Content-Type')
        if not content_type or 'multipart/form-data' not in content_type:
            return func.HttpResponse(
                json.dumps({"error": "Content-Type must be multipart/form-data"}),
                mimetype="application/json",
                status_code=400
            )

        body = req.get_body()
        multipart_data = decoder.MultipartDecoder(body, content_type)

        file_part = None
        for part in multipart_data.parts:
            if b'filename=' in part.headers.get(b'Content-Disposition', b''):
                file_part = part
                break

        if not file_part:
            return func.HttpResponse(
                json.dumps({"error": "No file uploaded"}),
                mimetype="application/json",
                status_code=400
            )

        content_disposition = file_part.headers[b'Content-Disposition'].decode()
        filename = content_disposition.split("filename=")[-1].strip("\"")
        ext = filename.lower().split('.')[-1]

        if ext not in ('xlsx', 'xls', 'csv'):
            return func.HttpResponse(
                json.dumps({"error": "Invalid file type. Please upload a .xlsx, .xls, or .csv file."}),
                mimetype="application/json",
                status_code=400
            )

        in_memory_file = io.BytesIO(file_part.content)
        in_memory_file.seek(0)

        if ext == 'csv':
            df = pd.read_csv(in_memory_file)
        else:
            df = pd.read_excel(in_memory_file)

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
