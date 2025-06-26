import json
import azure.functions as func
import pkgutil

def main(req: func.HttpRequest) -> func.HttpResponse:
    packages = [mod.name for mod in pkgutil.iter_modules()]
    return func.HttpResponse(json.dumps(packages), mimetype="application/json")
