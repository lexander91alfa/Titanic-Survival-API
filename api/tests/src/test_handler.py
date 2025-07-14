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
    def setup_test_environment(self):
        """Setup do ambiente de teste com todos os mocks necessários."""
        with patch("src.repository.passenger_repository.boto3") as mock_boto3, \
             patch("src.services.predict_service.PredictionService._load_model") as mock_load_model, \
             patch("prediction_handler.passenger_controller") as mock_passenger_controller:
            
            # Configurar mock do modelo
            mock_model = MagicMock()
            mock_model.predict_proba.return_value = [[0.3, 0.7]]  # 70% chance de sobrevivência
            mock_load_model.return_value = mock_model
            
            # Configurar mock do DynamoDB
            mock_table = MagicMock()
            mock_boto3.resource.return_value.Table.return_value = mock_table
            
            # Configurar mock do passenger_controller
            self.mock_passenger_controller = mock_passenger_controller
            
            yield

    def test_handler_post_success(self, passenger_repository):
        """
        Testa o handler da Lambda com um evento POST válido, mockando as dependências.
        """
        # Configure the mocked passenger controller
        mock_passenger = MagicMock()
        mock_passenger.id = "1"
        mock_passenger.probability = 0.7
        self.mock_passenger_controller.save_passenger.return_value = [mock_passenger]

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
        # Configure the mocked passenger controller for multiple passengers
        mock_passenger1 = MagicMock()
        mock_passenger1.model_dump.return_value = {"PassengerId": "1", "probability": 0.8}
        mock_passenger2 = MagicMock()
        mock_passenger2.model_dump.return_value = {"PassengerId": "2", "probability": 0.3}
        self.mock_passenger_controller.save_passenger.return_value = [mock_passenger1, mock_passenger2]
        
        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
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
        assert isinstance(body, list)
        assert len(body) == 2

    def test_handler_get_all_passengers(self, passenger_repository):
        """Testa GET para todos os passageiros."""
        # Configure the mocked passenger controller
        self.mock_passenger_controller.get_all_passengers.return_value = [
            {"passenger_id": "1", "survival_probability": 0.8},
            {"passenger_id": "2", "survival_probability": 0.3},
        ]
        
        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes",
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body) == 2

    def test_handler_get_passenger_by_id(self, passenger_repository):
        """Testa GET para um passageiro específico."""
        # Configure the mocked passenger controller
        self.mock_passenger_controller.get_passenger_by_id.return_value = {
            "passenger_id": "123",
            "survival_probability": 0.75,
        }
        
        test_event = {
            "httpMethod": "GET",
            "path": "/sobreviventes/123",
            "resource": "/sobreviventes/{id}",
            "pathParameters": {"id": "123"},
        }

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
            "pathParameters": {},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "ID do passageiro é obrigatório" in body["error"]

    def test_handler_delete_passenger(self, passenger_repository):
        """Testa DELETE de um passageiro."""
        # Configure the mocked passenger controller
        self.mock_passenger_controller.delete_passenger.return_value = {
            "message": "Passenger with ID 456 deleted successfully."
        }
        
        test_event = {
            "httpMethod": "DELETE",
            "path": "/sobreviventes/456",
            "pathParameters": {"id": "456"},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "deleted successfully" in body["message"]

    def test_handler_delete_passenger_missing_id(self, passenger_repository):
        """Testa DELETE sem ID."""
        test_event = {
            "httpMethod": "DELETE",
            "path": "/sobreviventes/",
            "pathParameters": {},
        }

        response = lambda_handler(test_event, None)

        assert response["statusCode"] == 400

    def test_handler_health_check_endpoint(self, passenger_repository):
        """Testa endpoint de health check."""
        test_event = {
            "httpMethod": "GET",
            "path": "/health",
        }

        with patch("prediction_handler.HealthCheck") as mock_health:
            mock_instance = MagicMock()
            mock_instance.get_overall_health.return_value = {
                "overall_status": "healthy",
                "components": {
                    "model": {"status": "healthy"},
                    "database": {"status": "healthy"},
                },
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

        with patch("prediction_handler.HealthCheck") as mock_health:
            mock_instance = MagicMock()
            mock_instance.get_overall_health.return_value = {
                "overall_status": "unhealthy",
                "components": {
                    "model": {"status": "unhealthy"},
                    "database": {"status": "healthy"},
                },
            }
            mock_health.return_value = mock_instance

            response = lambda_handler(test_event, None)

            assert response["statusCode"] == 503
            body = json.loads(response["body"])
            assert body["overall_status"] == "unhealthy"

    def test_handler_internal_server_error(self, passenger_repository):
        """Testa tratamento de erro interno do servidor."""
        # Configure the mocked passenger controller to raise Exception
        self.mock_passenger_controller.save_passenger.side_effect = Exception("Internal error")
        
        test_event = {
            "httpMethod": "POST",
            "path": "/sobreviventes",
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
