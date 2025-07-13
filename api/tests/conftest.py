# tests/conftest.py
import pytest
import os
import boto3
from moto import mock_aws
from unittest.mock import MagicMock

# Importa as classes do seu projeto
from src.repository.passenger_repository import PassengerRepository
from src.services.predict_service import PredictionService
from src.controllers.passenger_controller import PassengerController

# Garante que o boto3 não use credenciais reais durante os testes
@pytest.fixture(scope="module")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="module")
def dynamodb_table(aws_credentials):
    """Cria uma tabela DynamoDB mockada para os testes."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "titanic-survival-api-passengers"
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'passenger_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'passenger_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        yield table_name

@pytest.fixture
def passenger_repository(dynamodb_table):
    """Fixture para criar uma instância do repositório com a tabela mockada."""
    return PassengerRepository(table_name=dynamodb_table)

@pytest.fixture
def mock_prediction_service():
    """Cria um mock do serviço de predição."""
    mock_service = MagicMock(spec=PredictionService)
    # Configura o mock para retornar um valor fixo de probabilidade
    mock_service.predict.return_value = 0.85
    return mock_service

@pytest.fixture
def passenger_controller(mock_predict_service, passenger_repository):
    """Fixture para criar a instância do controller com dependências mockadas."""
    return PassengerController(
        prediction_service=mock_predict_service,
        repository=passenger_repository
    )