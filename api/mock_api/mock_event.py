from flask import json


def mock_post_passenger_event():
    return {
        "version": "2.0",
        "routeKey": "POST /sobreviventes",
        "rawPath": "/v1/sobreviventes",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "content-length": "122",
            "content-type": "application/json",
            "host": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "user-agent": "python-requests/2.32.3",
            "x-amzn-trace-id": "Root=1-6876633a-262e912431c96d923dc306d2",
            "x-api-key": "mdqLDXTIy76k1HQCQysnn3ODF0VOgN7b4O6iQZHD",
            "x-forwarded-for": "200.219.59.245",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "876042377474",
            "apiId": "rdogk5v2d1",
            "domainName": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "rdogk5v2d1",
            "http": {
                "method": "POST",
                "path": "/v1/sobreviventes",
                "protocol": "HTTP/1.1",
                "sourceIp": "200.219.59.245",
                "userAgent": "python-requests/2.32.3",
            },
            "requestId": "NwRxKjwmoAMEbPA=",
            "routeKey": "POST /sobreviventes",
            "stage": "v1",
            "time": "15/Jul/2025:14:18:34 +0000",
            "timeEpoch": 1752589114233,
        },
        "body": '[{"PassengerId": "1", "Pclass": 1, "Sex": "female", "Age": 40.0, "SibSp": 0, "Parch": 1, "Fare": 14.925, "Embarked": "S"}]',
        "isBase64Encoded": False,
    }


def mock_get_all_passengers_event():
    return {
        "version": "2.0",
        "routeKey": "GET /sobreviventes",
        "rawPath": "/v1/sobreviventes",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "content-length": "0",
            "content-type": "application/json",
            "host": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "user-agent": "python-requests/2.32.3",
            "x-amzn-trace-id": "Root=1-6876649f-338dfe1f44fd9d485117edd5",
            "x-api-key": "mdqLDXTIy76k1HQCQysnn3ODF0VOgN7b4O6iQZHD",
            "x-forwarded-for": "200.219.59.245",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "876042377474",
            "apiId": "rdogk5v2d1",
            "domainName": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "rdogk5v2d1",
            "http": {
                "method": "GET",
                "path": "/v1/sobreviventes",
                "protocol": "HTTP/1.1",
                "sourceIp": "200.219.59.245",
                "userAgent": "python-requests/2.32.3",
            },
            "requestId": "NwSo_j_qIAMEJfg=",
            "routeKey": "GET /sobreviventes",
            "stage": "v1",
            "time": "15/Jul/2025:14:24:31 +0000",
            "timeEpoch": 1752589471551,
        },
        "isBase64Encoded": False,
    }


def mock_get_passenger_by_id_event(passenger_id):
    return {
        "version": "2.0",
        "routeKey": "GET /sobreviventes/{id}",
        "rawPath": f"/v1/sobreviventes/{passenger_id}",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "content-length": "0",
            "content-type": "application/json",
            "host": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "user-agent": "python-requests/2.32.3",
            "x-amzn-trace-id": "Root=1-68766492-31e2ff5e2a1e2d8356993036",
            "x-api-key": "mdqLDXTIy76k1HQCQysnn3ODF0VOgN7b4O6iQZHD",
            "x-forwarded-for": "200.219.59.245",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "876042377474",
            "apiId": "rdogk5v2d1",
            "domainName": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "rdogk5v2d1",
            "http": {
                "method": "GET",
                "path": f"/v1/sobreviventes/{passenger_id}",
                "protocol": "HTTP/1.1",
                "sourceIp": "200.219.59.245",
                "userAgent": "python-requests/2.32.3",
            },
            "requestId": "NwSm7hCmIAMEcPw=",
            "routeKey": "GET /sobreviventes/{id}",
            "stage": "v1",
            "time": "15/Jul/2025:14:24:18 +0000",
            "timeEpoch": 1752589458387,
        },
        "pathParameters": {"id": str(passenger_id)},
        "isBase64Encoded": False,
    }


def mock_delete_passenger_event(passenger_id):
    return {
        "version": "2.0",
        "routeKey": "DELETE /sobreviventes/{id}",
        "rawPath": f"/v1/sobreviventes/{passenger_id}",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "content-length": "0",
            "content-type": "application/json",
            "host": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "user-agent": "python-requests/2.32.3",
            "x-amzn-trace-id": "Root=1-68766487-63e4f1226255cf70628e57c2",
            "x-api-key": "mdqLDXTIy76k1HQCQysnn3ODF0VOgN7b4O6iQZHD",
            "x-forwarded-for": "200.219.59.245",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "876042377474",
            "apiId": "rdogk5v2d1",
            "domainName": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "rdogk5v2d1",
            "http": {
                "method": "DELETE",
                "path": f"/v1/sobreviventes/{passenger_id}",
                "protocol": "HTTP/1.1",
                "sourceIp": "200.219.59.245",
                "userAgent": "python-requests/2.32.3",
            },
            "requestId": "NwSlTh0uoAMEcFg=",
            "routeKey": "DELETE /sobreviventes/{id}",
            "stage": "v1",
            "time": "15/Jul/2025:14:24:07 +0000",
            "timeEpoch": 1752589447974,
        },
        "pathParameters": {"id": str(passenger_id)},
        "isBase64Encoded": False,
    }


def mock_health_check_event():
    return {
        "version": "2.0",
        "routeKey": "GET /health",
        "rawPath": "/v1/health",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "content-length": "0",
            "content-type": "application/json",
            "host": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "user-agent": "python-requests/2.32.3",
            "x-amzn-trace-id": "Root=1-6876649f-338dfe1f44fd9d485117edd5",
            "x-api-key": "mdqLDXTIy76k1HQCQysnn3ODF0VOgN7b4O6iQZHD",
            "x-forwarded-for": "200.219.59.245",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "876042377474",
            "apiId": "rdogk5v2d1",
            "domainName": "rdogk5v2d1.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "rdogk5v2d1",
            "http": {
                "method": "GET",
                "path": "/v1/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "200.219.59.245",
                "userAgent": "python-requests/2.32.3",
            },
            "requestId": "NwSo_j_qIAMEJfg=",
            "routeKey": "GET /health",
            "stage": "v1",
            "time": "15/Jul/2025:14:24:31 +0000",
            "timeEpoch": 1752589471551,
        },
        "isBase64Encoded": False,
    }
