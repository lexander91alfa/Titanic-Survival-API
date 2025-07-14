import json
import pytest
from unittest.mock import patch, MagicMock
from prediction_handler import lambda_handler


class TestLambdaHandler:
    """Testes para o lambda_handler."""


    def test_handler_post_success(self, passenger_repository):
        """
        Testa o handler da Lambda com um evento POST válido, mockando as dependências.
        """

        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "body": json.dumps(
                {
                    "PassengerId": "1",
                    "Pclass": 1,
                    "Sex": "female",
                    "Age": 38.0,
                    "SibSp": 1,
                    "Parch": 0,
                    "Fare": 71.2833,
                    "Embarked": "C",
                }
            ),
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert "PassengerId" in body
        assert "probability" in body
        assert isinstance(body["probability"], float)

    def test_handler_validation_error(self, passenger_repository):
        """
        Testa se o handler retorna um erro 422 para uma requisição com dados inválidos.
        """

        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "body": json.dumps({"Pclass": 99, "Sex": "alien", "Age": -10}),
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 422
        body = json.loads(response["body"])
        assert body["error"] is True

    def test_handler_post_multiple_passengers(self, passenger_repository):
        """Testa POST com múltiplos passageiros."""
        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "body": json.dumps([
                {
                    "PassengerId": "1",
                    "Pclass": 1,
                    "Sex": "female",
                    "Age": 25.0,
                    "SibSp": 0,
                    "Parch": 1,
                    "Fare": 100.0,
                    "Embarked": "S",
                },
                {
                    "PassengerId": "2",
                    "Pclass": 3,
                    "Sex": "male",
                    "Age": 30.0,
                    "SibSp": 1,
                    "Parch": 0,
                    "Fare": 20.0,
                    "Embarked": "Q",
                }
            ]),
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert isinstance(body, list)
        assert len(body) == 2

    def test_handler_get_all_passengers(self, passenger_repository):
        """Testa GET para todos os passageiros."""
        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes",
        }

        with patch('prediction_handler.PassengerController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_passengers.return_value = [
                {"passenger_id": "1", "survival_probability": 0.8},
                {"passenger_id": "2", "survival_probability": 0.3}
            ]
            mock_controller.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert len(body) == 2

    def test_handler_get_passenger_by_id(self, passenger_repository):
        """Testa GET para um passageiro específico."""
        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes/123",
            "resource": "/sobreviventes/{id}",
            "pathParameters": {"id": "123"}
        }

        with patch('prediction_handler.PassengerController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_passenger_by_id.return_value = {
                "passenger_id": "123",
                "survival_probability": 0.75
            }
            mock_controller.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["passenger_id"] == "123"

    def test_handler_get_passenger_by_id_missing_parameter(self, passenger_repository):
        """Testa GET com ID ausente."""
        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes/",
            "resource": "/sobreviventes/{id}",
            "pathParameters": {}
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "ID do passageiro é obrigatório" in body["error"]

    def test_handler_delete_passenger(self, passenger_repository):
        """Testa DELETE de um passageiro."""
        test_event = {
            "httpMethod": "DELETE",
            "path": "/sobreviventes/456",
            "pathParameters": {"id": "456"}
        }

        with patch('prediction_handler.PassengerController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.delete_passenger.return_value = {
                "message": "Passenger with ID 456 deleted successfully."
            }
            mock_controller.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert "deleted successfully" in body["message"]

    def test_handler_delete_passenger_missing_id(self, passenger_repository):
        """Testa DELETE sem ID."""
        test_event = {
            "httpMethod": "DELETE",
            "path": "/sobreviventes/",
            "pathParameters": {}
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] is True

    def test_handler_unsupported_method(self, passenger_repository):
        """Testa método HTTP não suportado."""
        test_event = {
            "httpMethod": "PATCH",
            "path": "/sobreviventes",
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 405
        body = json.loads(response["body"])
        assert body["error"] is True
        assert "Método HTTP não permitido" in body["message"]

    def test_handler_health_check_endpoint(self, passenger_repository):
        """Testa endpoint de health check."""
        test_event = {
            "httpMethod": "GET",
            "path": "/health",
        }

        with patch('prediction_handler.HealthCheck') as mock_health:
            mock_instance = MagicMock()
            mock_instance.get_overall_health.return_value = {
                "overall_status": "healthy",
                "components": {
                    "model": {"status": "healthy"},
                    "database": {"status": "healthy"}
                }
            }
            mock_health.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["overall_status"] == "healthy"

    def test_handler_health_check_unhealthy(self, passenger_repository):
        """Testa endpoint de health check com sistema não saudável."""
        test_event = {
            "httpMethod": "GET",
            "path": "/health",
        }

        with patch('prediction_handler.HealthCheck') as mock_health:
            mock_instance = MagicMock()
            mock_instance.get_overall_health.return_value = {
                "overall_status": "unhealthy",
                "components": {
                    "model": {"status": "unhealthy"},
                    "database": {"status": "healthy"}
                }
            }
            mock_health.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 503
            body = json.loads(response["body"])
            assert body["overall_status"] == "unhealthy"

    def test_handler_internal_server_error(self, passenger_repository):
        """Testa tratamento de erro interno do servidor."""
        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "body": json.dumps({
                "PassengerId": "error_test",
                "Pclass": 1,
                "Sex": "female",
                "Age": 30.0,
                "SibSp": 0,
                "Parch": 0,
                "Fare": 50.0,
                "Embarked": "S",
            }),
        }

        with patch('prediction_handler.PassengerController') as mock_controller:
            mock_controller.side_effect = Exception("Internal error")

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 500
            body = json.loads(response["body"])
            assert body["error"] is True
            assert body["message"] == "Erro interno do servidor"

    def test_handler_business_error(self, passenger_repository):
        """Testa tratamento de erro de negócio."""
        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "body": json.dumps({
                "PassengerId": "business_error_test",
                "Pclass": 1,
                "Sex": "female",
                "Age": 30.0,
                "SibSp": 0,
                "Parch": 0,
                "Fare": 50.0,
                "Embarked": "S",
            }),
        }

        with patch('prediction_handler.PassengerController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.save_passenger.side_effect = ValueError("Business rule violation")
            mock_controller.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 400
            body = json.loads(response["body"])
            assert body["error"] is True
            assert "Business rule violation" in body["message"]
