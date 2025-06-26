import logging
import azure.functions as func
import os
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing feedback submission.')

    try:
        req_body = req.get_json()
        name = req_body.get('name')
        feedback = req_body.get('feedback')

        if not name or not feedback:
            return func.HttpResponse("Missing 'name' or 'feedback'", status_code=400)

        api_key = os.environ.get("BACKEND_API_KEY_DEFAULT")
        if not api_key:
            return func.HttpResponse("API key not configured in environment", status_code=500)

        response = requests.post(
            f"https://your-upstream-api.net/feedback?code={api_key}",
            json={"name": name, "feedback": feedback},
            headers={"Accept": "application/json"}
        )

        return func.HttpResponse(response.text, status_code=response.status_code)

    except ValueError:
        return func.HttpResponse("Invalid JSON input", status_code=400)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse("Something went wrong processing your request.", status_code=500)