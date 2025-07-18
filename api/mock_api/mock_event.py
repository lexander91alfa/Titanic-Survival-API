import json
import base64


def _get_common_context(http_method, path, resource_path):
    """Helper to create a common request context for v1.0 payload."""
    return {
        "accountId": "123456789012",
        "resourceId": "123456",
        "stage": "prod",
        "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
        "requestTime": "09/Apr/2015:12:34:56 +0000",
        "requestTimeEpoch": 1428582896000,
        "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "accessKey": None,
            "sourceIp": "127.0.0.1",
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "Custom User Agent String",
            "user": None,
        },
        "path": f"/prod{path}",
        "resourcePath": resource_path,
        "httpMethod": http_method,
        "apiId": "1234567890",
        "protocol": "HTTP/1.1",
    }


def _get_common_headers():
    """Helper to create common headers."""
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
        "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
        "User-Agent": "python-requests/2.32.3",
        "X-Forwarded-For": "127.0.0.1",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https",
    }
    return headers, {k: [v] for k, v in headers.items()}


def mock_post_passenger_event(body=None):
    path = "/sobreviventes"
    resource_path = "/sobreviventes"
    http_method = "POST"
    headers, multi_value_headers = _get_common_headers()

    body_str = json.dumps(body) if body else None

    return {
        "body": body_str,
        "resource": resource_path,
        "path": path,
        "httpMethod": http_method,
        "isBase64Encoded": False,
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "headers": headers,
        "multiValueHeaders": multi_value_headers,
        "requestContext": _get_common_context(http_method, path, resource_path),
    }


def mock_get_all_passengers_event():
    path = "/sobreviventes"
    resource_path = "/sobreviventes"
    http_method = "GET"
    headers, multi_value_headers = _get_common_headers()

    return {
        "body": None,
        "resource": resource_path,
        "path": path,
        "httpMethod": http_method,
        "isBase64Encoded": False,
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "headers": headers,
        "multiValueHeaders": multi_value_headers,
        "requestContext": _get_common_context(http_method, path, resource_path),
    }


def mock_get_passenger_by_id_event(passenger_id):
    path = f"/sobreviventes/{passenger_id}"
    resource_path = "/sobreviventes/{id}"
    http_method = "GET"
    headers, multi_value_headers = _get_common_headers()
    path_params = {"id": str(passenger_id)}

    return {
        "body": None,
        "resource": resource_path,
        "path": path,
        "httpMethod": http_method,
        "isBase64Encoded": False,
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": path_params,
        "stageVariables": None,
        "headers": headers,
        "multiValueHeaders": multi_value_headers,
        "requestContext": _get_common_context(http_method, path, resource_path),
    }


def mock_delete_passenger_event(passenger_id):
    path = f"/sobreviventes/{passenger_id}"
    resource_path = "/sobreviventes/{id}"
    http_method = "DELETE"
    headers, multi_value_headers = _get_common_headers()
    path_params = {"id": str(passenger_id)}

    return {
        "body": None,
        "resource": resource_path,
        "path": path,
        "httpMethod": http_method,
        "isBase64Encoded": False,
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": path_params,
        "stageVariables": None,
        "headers": headers,
        "multiValueHeaders": multi_value_headers,
        "requestContext": _get_common_context(http_method, path, resource_path),
    }


def mock_health_check_event():
    path = "/health"
    resource_path = "/health"
    http_method = "GET"
    headers, multi_value_headers = _get_common_headers()

    return {
        "body": None,
        "resource": resource_path,
        "path": path,
        "httpMethod": http_method,
        "isBase64Encoded": False,
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "headers": headers,
        "multiValueHeaders": multi_value_headers,
        "requestContext": _get_common_context(http_method, path, resource_path),
    }
