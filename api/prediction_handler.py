import json

def create_response(status_code, body):
    """Cria uma resposta HTTP formatada para o API Gateway."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" # Permite CORS para testes
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    http_method = event.get('httpMethod')
    path = event.get('path')

    return create_response(200, {"message": "Hello from Lambda!", "httpMethod": http_method, "path": path})