from flask import json


def mock_post_passenger_event():
    return {
        "body": json.dumps({"PassengerId": "1", "Pclass": 3, "Sex": "female", "Age": 26.0, "SibSp": 0, "Parch": 0, "Fare": 7.925}),
        "resource": "/sobreviventes",
        "path": "/sobreviventes",
        "httpMethod": "POST",
        "isBase64Encoded": False,
        "queryStringParameters": {},
        "pathParameters": {},
        "stageVariables": {
            "stage": "v1"
        },
        "headers": {
            "Content-Type": "application/json",
            "x-api-key": "SUA_CHAVE_DE_API_AQUI"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "res001",
            "stage": "v1",
            "requestId": "reqid-001",
            "identity": {
            "sourceIp": "203.0.113.1"
            },
            "path": "/v1/sobreviventes",
            "resourcePath": "/sobreviventes",
            "httpMethod": "POST",
            "apiId": "api123"
        }
    }

def mock_get_all_passengers_event():
    return {
        "body": None,
        "resource": "/sobreviventes",
        "path": "/sobreviventes",
        "httpMethod": "GET",
        "isBase64Encoded": False,
        "queryStringParameters": {},
        "pathParameters": {},
        "stageVariables": {
            "stage": "v1"
        },
        "headers": {
            "x-api-key": "SUA_CHAVE_DE_API_AQUI"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "res001",
            "stage": "v1",
            "requestId": "reqid-002",
            "identity": {
            "sourceIp": "203.0.113.2"
            },
            "path": "/v1/sobreviventes",
            "resourcePath": "/sobreviventes",
            "httpMethod": "GET",
            "apiId": "api123"
        }
    }

def mock_get_passenger_by_id_event(passenger_id):
    return {
        "body": None,
        "resource": f"/sobreviventes/{passenger_id}",
        "path": f"/sobreviventes/{passenger_id}",
        "httpMethod": "GET",
        "isBase64Encoded": False,
        "queryStringParameters": {},
        "pathParameters": {
            "id": passenger_id
        },
        "stageVariables": {
            "stage": "v1"
        },
        "headers": {
            "x-api-key": "SUA_CHAVE_DE_API_AQUI"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "res001",
            "stage": "v1",
            "requestId": f"reqid-{passenger_id}",
            "identity": {
            "sourceIp": f"203.0.113.{int(passenger_id) + 2}"
            },
            "path": f"/v1/sobreviventes/{passenger_id}",
            "resourcePath": "/sobreviventes/{id}",
            "httpMethod": "GET",
            "apiId": "api123"
        }
    }

def mock_delete_passenger_event(passenger_id):
    return {
        "body": None,
        "resource": f"/sobreviventes/{passenger_id}",
        "path": f"/sobreviventes/{passenger_id}",
        "httpMethod": "DELETE",
        "isBase64Encoded": False,
        "queryStringParameters": {},
        "pathParameters": {
            "id": passenger_id
        },
        "stageVariables": {
            "stage": "v1"
        },
        "headers": {
            "x-api-key": "SUA_CHAVE_DE_API_AQUI"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "res001",
            "stage": "v1",
            "requestId": f"reqid-{passenger_id}",
            "identity": {
            "sourceIp": f"203.0.113.{int(passenger_id) + 2}"
            },
            "path": f"/v1/sobreviventes/{passenger_id}",
            "resourcePath": "/sobreviventes/{id}",
            "httpMethod": "DELETE",
            "apiId": "api123"
        }
    }