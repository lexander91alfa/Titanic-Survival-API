from src.models.passeger_request import PassengerRequest
from src.services.predict_service import PredictionService
from src.adapter.http_adapter import HTTPAdapter


prediction_service = PredictionService(model_name="model")


def lambda_handler(event, _):
    """Função Lambda para lidar com requisições HTTP."""
    http_handler = HTTPAdapter(event)
    http_method = http_handler.method

    match http_method:
        case "POST":
            request_data = http_handler.body
            passenger = [PassengerRequest(**data) for data in request_data]
            prediction = [{ "survival_probability": prediction_service.predict(p) } for p in passenger]
            return http_handler.build_response(
                200, {"survival_probability": prediction}
            )

        case "GET":
            pass


if __name__ == "__main__":
    # Testando a função localmente
    from pprint import pprint

    test_event = [
        {
            "body": '[{"Pclass": 3, "Sex": "female", "Age": 26.0, "SibSp": 0, "Parch": 1, "Fare": 7.925, "Embarked": "C"}, {"Pclass": 1, "Sex": "male", "Age": 22.0, "SibSp": 1, "Parch": 0, "Fare": 71.2833, "Embarked": "S"}]',
            "resource": "/sobreviventes",
            "path": "/sobreviventes",
            "httpMethod": "POST",
            "isBase64Encoded": False,
            "queryStringParameters": {},
            "pathParameters": {},
            "stageVariables": {"stage": "v1"},
            "headers": {
                "Content-Type": "application/json",
                "x-api-key": "SUA_CHAVE_DE_API_AQUI",
            },
            "requestContext": {
                "accountId": "123456789012",
                "resourceId": "res001",
                "stage": "v1",
                "requestId": "reqid-001",
                "identity": {"sourceIp": "203.0.113.1"},
                "path": "/v1/sobreviventes",
                "resourcePath": "/sobreviventes",
                "httpMethod": "POST",
                "apiId": "api123",
            },
        },
        {
            "body": None,
            "resource": "/sobreviventes/{id}",
            "path": "/sobreviventes/1",
            "httpMethod": "GET",
            "isBase64Encoded": False,
            "queryStringParameters": {},
            "pathParameters": {"id": "1"},
            "stageVariables": {"stage": "v1"},
            "headers": {"x-api-key": "SUA_CHAVE_DE_API_AQUI"},
            "requestContext": {
                "accountId": "123456789012",
                "resourceId": "res002",
                "stage": "v1",
                "requestId": "reqid-003",
                "identity": {"sourceIp": "203.0.113.3"},
                "path": "/v1/sobreviventes/a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "resourcePath": "/sobreviventes/{id}",
                "httpMethod": "GET",
                "apiId": "api123",
            },
        },
    ]
    response = lambda_handler(test_event[0], None)
    pprint(response)
