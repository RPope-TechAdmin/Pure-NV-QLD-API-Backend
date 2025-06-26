import pkgutil
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    available = [mod.name for mod in pkgutil.iter_modules()]
    return func.HttpResponse(
        json.dumps(available),
        mimetype="application/json"
    )
