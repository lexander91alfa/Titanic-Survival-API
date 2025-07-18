from decimal import Decimal
import json
import pytest
import os
from unittest.mock import patch, MagicMock

# Set environment variable before any imports
os.environ["DYNAMODB_TABLE_NAME"] = "test-table"

# Import after the environment is set
from prediction_handler import lambda_handler


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure test environment variables are set for the entire test session."""
    # Backup original value if it exists
    original_value = os.environ.get("DYNAMODB_TABLE_NAME")

    # Set test value
    os.environ["DYNAMODB_TABLE_NAME"] = "test-table"

    yield

    # Restore original value or remove if it didn't exist
    if original_value is not None:
        os.environ["DYNAMODB_TABLE_NAME"] = original_value
    else:
        os.environ.pop("DYNAMODB_TABLE_NAME", None)


class TestLambdaHandler:
    """Testes para o lambda_handler."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setup dos mocks necessários para os testes."""
        # Mock para o repositório
        with patch("src.repository.passenger_repository.boto3") as mock_boto3:
            mock_table = MagicMock()
            mock_boto3.resource.return_value.Table.return_value = mock_table
            yield mock_table

    @pytest.fixture(autouse=True)
    def setup_prediction_service(self):
        """Setup do serviço de predição."""
        with patch(
            "src.services.predict_service.PredictionService._load_model"
        ) as mock_load_model:
            mock_model = MagicMock()
            mock_model.predict_proba.return_value = [
                [0.3, 0.7]
            ]  # 70% chance de sobrevivência
            mock_load_model.return_value = mock_model
            yield mock_model

    @pytest.fixture(autouse=True)
    def setup_controller(self):
        """Setup do controller de passageiros."""
        with patch(
            "prediction_handler.passenger_controller"
        ) as mock_passenger_controller:
            self.mock_passenger_controller = mock_passenger_controller
            yield mock_passenger_controller

    def test_handler_post_success(self, passenger_repository):
        """
        Testa o handler da Lambda com um evento POST válido.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "passenger_id": "1",
            "survival_probability": 0.7,
            "prediction": "survived",
            "confidence_level": "medium",
        }
        self.mock_passenger_controller.save_passenger.return_value = [mock_response]

        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "headers": {"Content-Type": "application/json"},
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
        assert body["success"] is True
        assert body["message"] == "Predição de sobrevivência realizada com sucesso"
        assert "data" in body
        assert "passenger_id" in body["data"]
        assert "survival_probability" in body["data"]

    def test_handler_validation_error(self, passenger_repository):
        """
        Testa se o handler retorna um erro 422 para uma requisição com dados inválidos.
        """
        # Arrange
        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"Pclass": 99, "Sex": "alien", "Age": -10}),
        }

        # Act
        response = lambda_handler(test_event, None)

        # Assert
        assert response["statusCode"] == 422
        body = json.loads(response["body"])
        assert body["error"] is True
        assert "Erro de validação nos dados fornecidos" in body["message"]

    def test_handler_post_multiple_passengers(self, passenger_repository):
        """Testa POST com múltiplos passageiros."""
        # Arrange
        mock_responses = [
            MagicMock(
                model_dump=lambda: {
                    "passenger_id": "1",
                    "survival_probability": 0.8,
                    "prediction": "survived",
                    "confidence_level": "high",
                }
            ),
            MagicMock(
                model_dump=lambda: {
                    "passenger_id": "2",
                    "survival_probability": 0.3,
                    "prediction": "not_survived",
                    "confidence_level": "medium",
                }
            ),
        ]
        self.mock_passenger_controller.save_passenger.return_value = mock_responses

        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                [
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
                    },
                ]
            ),
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Predições de sobrevivência realizadas com sucesso"
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 2

    def test_handler_get_all_passengers(self, passenger_repository):
        """Testa GET para todos os passageiros."""
        # Arrange
        mock_result = {
            "items": [
                {
                    "passenger_id": "1",
                    "survival_probability": 0.8,
                    "prediction": "survived",
                    "confidence_level": "high",
                },
                {
                    "passenger_id": "2",
                    "survival_probability": 0.3,
                    "prediction": "not_survived",
                    "confidence_level": "medium",
                },
            ],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total_items": 2,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            },
        }
        self.mock_passenger_controller.get_all_passengers.return_value = mock_result

        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes",
            "headers": {"Content-Type": "application/json"},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Lista de passageiros recuperada com sucesso"
        assert "data" in body
        assert "passengers" in body["data"]
        assert "pagination" in body["data"]
        assert len(body["data"]["passengers"]) == 2

    def test_handler_get_passenger_by_id(self, passenger_repository):
        """Testa GET para um passageiro específico."""
        # Arrange
        mock_passenger = {
            "passenger_id": "123",
            "survival_probability": 0.75,
            "prediction": "survived",
            "confidence_level": "medium",
            "created_at": "2025-07-17T10:00:00Z",
            "updated_at": "2025-07-17T10:00:00Z",
        }
        self.mock_passenger_controller.get_passenger_by_id.return_value = mock_passenger

        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes/123",
            "resource": "/sobreviventes/{id}",
            "pathParameters": {"id": "123"},
            "headers": {"Content-Type": "application/json"},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Dados do passageiro recuperados com sucesso"
        assert "data" in body
        assert body["data"]["passenger_id"] == "123"

    def test_handler_get_passenger_by_id_missing_parameter(self, passenger_repository):
        """Testa GET com ID ausente."""
        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes/",
            "resource": "/sobreviventes/{id}",
            "pathParameters": {},
            "headers": {"Content-Type": "application/json"},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] is True
        assert "ID do passageiro é obrigatório" in body["message"]

    def test_handler_delete_passenger(self, passenger_repository):
        """Testa DELETE de um passageiro."""
        # Arrange
        from src.models.api_response import DeleteResponse

        mock_delete_response = DeleteResponse(
            deleted=True,
            passenger_id="456",
            message="Passageiro com ID 456 excluído com sucesso.",
        )
        self.mock_passenger_controller.delete_passenger.return_value = (
            mock_delete_response
        )

        test_event = {
            "httpMethod": "DELETE",
            "path": "/sobreviventes/456",
            "pathParameters": {"id": "456"},
            "headers": {"Content-Type": "application/json"},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Passageiro excluído com sucesso"
        assert "data" in body
        assert body["data"]["deleted"] is True
        assert body["data"]["passenger_id"] == "456"

    def test_handler_delete_passenger_missing_id(self, passenger_repository):
        """Testa DELETE sem ID."""
        test_event = {
            "httpMethod": "DELETE",
            "path": "/sobreviventes/",
            "pathParameters": {},
            "headers": {"Content-Type": "application/json"},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400

    def test_handler_health_check_endpoint(self, passenger_repository):
        """Testa endpoint de health check."""
        # Arrange
        test_event = {
            "httpMethod": "GET",
            "path": "/health",
            "headers": {"Content-Type": "application/json"},
        }

        mock_health_status = {
            "overall_status": "healthy",
            "components": {
                "model": {"status": "healthy", "message": "Model is working"},
                "database": {"status": "healthy", "message": "Database is working"},
            },
        }

        with patch("prediction_handler.HealthCheck") as mock_health:
            # Arrange
            mock_instance = MagicMock()
            mock_instance.get_overall_health.return_value = mock_health_status
            mock_health.return_value = mock_instance

            # Act
            response = lambda_handler(test_event, None)

            # Assert
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["overall_status"] == "healthy"
            assert "components" in body
            assert "metadata" in body
            assert body["components"]["model"]["status"] == "healthy"
            assert body["components"]["database"]["status"] == "healthy"

    def test_handler_health_check_unhealthy(self, passenger_repository):
        """Testa endpoint de health check com sistema não saudável."""
        test_event = {
            "httpMethod": "GET",
            "path": "/health",
            "headers": {"Content-Type": "application/json"},
        }

        with patch("prediction_handler.HealthCheck") as mock_health:
            mock_instance = MagicMock()
            mock_instance.get_overall_health.return_value = {
                "overall_status": "unhealthy",
                "components": {
                    "model": {"status": "unhealthy", "message": "Model not working"},
                    "database": {"status": "healthy", "message": "Database is working"},
                },
            }
            mock_health.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 503
            body = json.loads(response["body"])
            assert body["overall_status"] == "unhealthy"

    def test_handler_internal_server_error(self, passenger_repository):
        """Testa tratamento de erro interno do servidor."""
        # Arrange
        self.mock_passenger_controller.save_passenger.side_effect = Exception(
            "Erro interno do servidor"
        )

        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "PassengerId": "error_test",
                    "Pclass": 1,
                    "Sex": "female",
                    "Age": 30.0,
                    "SibSp": 0,
                    "Parch": 0,
                    "Fare": 50.0,
                    "Embarked": "S",
                }
            ),
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["error"] is True
        assert body["message"] == "Erro interno do servidor"

    def test_handler_business_error(self, passenger_repository):
        """Testa tratamento de erro de negócio."""
        # Configure the mocked passenger controller to raise ValueError
        self.mock_passenger_controller.save_passenger.side_effect = ValueError(
            "Business rule violation"
        )

        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "PassengerId": "business_error_test",
                    "Pclass": 1,
                    "Sex": "female",
                    "Age": 30.0,
                    "SibSp": 0,
                    "Parch": 0,
                    "Fare": 50.0,
                    "Embarked": "S",
                }
            ),
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] is True
        assert "Business rule violation" in body["message"]
