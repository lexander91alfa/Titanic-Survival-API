import pytest
import json
from src.adapter.http_adapter import HTTPAdapter
from src.models.prediction_response import PredictionResponse


class TestHTTPAdapter:
    """Testes para a classe HTTPAdapter."""

    def test_adapter_initialization(self):
        """Testa inicialização do adapter."""
        event = {
            "httpMethod": "GET",
            "path": "/test",
            "body": None
        }
        
        adapter = HTTPAdapter(event)
        assert adapter._event == event
        assert adapter._body is None

    def test_method_property(self):
        """Testa propriedade method."""
        event = {"httpMethod": "POST"}
        adapter = HTTPAdapter(event)
        assert adapter.method == "POST"

    def test_method_property_missing(self):
        """Testa propriedade method quando ausente."""
        event = {}
        adapter = HTTPAdapter(event)
        assert adapter.method is None

    def test_path_property(self):
        """Testa propriedade path."""
        event = {"path": "/sobreviventes"}
        adapter = HTTPAdapter(event)
        assert adapter.path == "/sobreviventes"

    def test_path_property_missing(self):
        """Testa propriedade path quando ausente."""
        event = {}
        adapter = HTTPAdapter(event)
        assert adapter.path is None

    def test_path_parameters_property(self):
        """Testa propriedade path_parameters."""
        event = {"pathParameters": {"id": "123", "type": "passenger"}}
        adapter = HTTPAdapter(event)
        assert adapter.path_parameters == {"id": "123", "type": "passenger"}

    def test_path_parameters_property_missing(self):
        """Testa propriedade path_parameters quando ausente."""
        event = {}
        adapter = HTTPAdapter(event)
        assert adapter.path_parameters == {}

    def test_path_parameters_property_null(self):
        """Testa propriedade path_parameters quando é null."""
        event = {"pathParameters": None}
        adapter = HTTPAdapter(event)
        assert adapter.path_parameters == {}

    def test_resource_property(self):
        """Testa propriedade resource."""
        event = {"resource": "/sobreviventes/{id}"}
        adapter = HTTPAdapter(event)
        assert adapter.resource == "/sobreviventes/{id}"

    def test_resource_property_missing(self):
        """Testa propriedade resource quando ausente."""
        event = {}
        adapter = HTTPAdapter(event)
        assert adapter.resource is None

    def test_body_property_valid_json(self):
        """Testa propriedade body com JSON válido."""
        test_data = {"name": "test", "value": 123}
        event = {"body": json.dumps(test_data)}
        adapter = HTTPAdapter(event)
        
        assert adapter.body == test_data

    def test_body_property_invalid_json(self):
        """Testa propriedade body com JSON inválido."""
        event = {"body": "invalid json"}
        adapter = HTTPAdapter(event)
        
        assert adapter.body == {}

    def test_body_property_empty(self):
        """Testa propriedade body quando vazio."""
        event = {"body": ""}
        adapter = HTTPAdapter(event)
        
        assert adapter.body == {}

    def test_body_property_null(self):
        """Testa propriedade body quando é null."""
        event = {"body": None}
        adapter = HTTPAdapter(event)
        
        assert adapter.body == {}

    def test_body_property_missing(self):
        """Testa propriedade body quando ausente."""
        event = {}
        adapter = HTTPAdapter(event)
        
        assert adapter.body == {}

    def test_body_property_caching(self):
        """Testa se o body é cached após primeira chamada."""
        test_data = {"cached": True}
        event = {"body": json.dumps(test_data)}
        adapter = HTTPAdapter(event)
        
        # Primeira chamada
        first_call = adapter.body
        # Segunda chamada
        second_call = adapter.body
        
        assert first_call == second_call
        assert first_call is second_call  # Mesmo objeto

    def test_build_response_with_dict(self):
        """Testa build_response com dicionário."""
        data = {"message": "success", "count": 10}
        response = HTTPAdapter.build_response(200, data)
        
        expected = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(data),
        }
        
        assert response == expected

    def test_build_response_with_list(self):
        """Testa build_response com lista."""
        data = [{"id": 1}, {"id": 2}]
        response = HTTPAdapter.build_response(201, data)
        
        assert response["statusCode"] == 201
        assert json.loads(response["body"]) == data

    def test_build_response_with_pydantic_model(self):
        """Testa build_response com modelo Pydantic."""
        prediction = PredictionResponse(id="test_id", probability=0.75)
        response = HTTPAdapter.build_response(200, prediction)
        
        expected_body = {"id": "test_id", "probability": 0.75}
        
        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == expected_body

    def test_build_response_with_string(self):
        """Testa build_response com string."""
        message = "Operation completed"
        response = HTTPAdapter.build_response(200, message)
        
        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == message

    def test_build_response_with_none(self):
        """Testa build_response com None."""
        response = HTTPAdapter.build_response(204, None)
        
        assert response["statusCode"] == 204
        assert json.loads(response["body"]) is None

    def test_build_response_cors_headers(self):
        """Testa se headers CORS estão incluídos."""
        response = HTTPAdapter.build_response(200, {})
        
        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"
        assert response["headers"]["Content-Type"] == "application/json"

    def test_build_response_different_status_codes(self):
        """Testa build_response com diferentes códigos de status."""
        test_cases = [
            (200, "OK"),
            (201, "Created"),
            (400, "Bad Request"),
            (404, "Not Found"),
            (500, "Internal Server Error")
        ]
        
        for status_code, message in test_cases:
            response = HTTPAdapter.build_response(status_code, {"message": message})
            assert response["statusCode"] == status_code

    def test_complex_event_parsing(self):
        """Testa parsing de evento complexo do API Gateway."""
        complex_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes/123/predictions",
            "resource": "/sobreviventes/{id}/predictions",
            "pathParameters": {
                "id": "123"
            },
            "queryStringParameters": {
                "format": "json",
                "include": "metadata"
            },
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer token123"
            },
            "body": json.dumps({
                "PassengerId": "123",
                "Pclass": 1,
                "Sex": "female",
                "Age": 30.0,
                "SibSp": 0,
                "Parch": 1,
                "Fare": 100.0,
                "Embarked": "S"
            })
        }
        
        adapter = HTTPAdapter(complex_event)
        
        assert adapter.method == "POST"
        assert adapter.path == "/sobreviventes/123/predictions"
        assert adapter.resource == "/sobreviventes/{id}/predictions"
        assert adapter.path_parameters["id"] == "123"
        assert adapter.body["PassengerId"] == "123"
        assert adapter.body["Pclass"] == 1

    def test_empty_event_handling(self):
        """Testa handling de evento vazio."""
        adapter = HTTPAdapter({})
        
        assert adapter.method is None
        assert adapter.path is None
        assert adapter.resource is None
        assert adapter.path_parameters == {}
        assert adapter.body == {}
