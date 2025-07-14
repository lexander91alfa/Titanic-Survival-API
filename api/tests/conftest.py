from pytest import fixture
import os
import boto3
from moto import mock_aws
from unittest.mock import MagicMock, patch
import os

from src.repository.passenger_repository import PassengerRepository
from src.services.predict_service import PredictionService
from src.controllers.passenger_controller import PassengerController


@fixture(scope="module", autouse=True)
def aws_credentials():
    """Define credenciais AWS falsas para os testes."""
    os.environ["DYNAMODB_TABLE_NAME"] = "titanic-survival-api-passengers"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_REGION"] = "us-east-1"
    yield


@fixture(scope="function")
def dynamodb_table():
    """Cria uma tabela DynamoDB mockada para os testes."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "titanic-survival-api-passengers"
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "passenger_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "passenger_id", "AttributeType": "S"}
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        yield


@fixture
def passenger_repository(dynamodb_table):
    """Fixture para criar uma instância do repositório com a tabela mockada."""
    return PassengerRepository()


@fixture
def passenger_controller(passenger_repository):
    """Fixture para criar a instância do controller com dependências mockadas."""
    return PassengerController()


@fixture
def mock_prediction_service():
    """Fixture para criar um mock do serviço de predição."""
    with patch("src.services.predict_service.PredictionService") as mock_service:
        mock_instance = MagicMock()
        mock_instance.predict.return_value = 0.75
        mock_service.return_value = mock_instance
        yield mock_instance


@fixture
def sample_passenger_data():
    """Fixture com dados de exemplo de passageiro."""
    return {
        "PassengerId": "test_123",
        "Pclass": 1,
        "Sex": "female",
        "Age": 30.0,
        "SibSp": 0,
        "Parch": 1,
        "Fare": 100.0,
        "Embarked": "S",
    }


@fixture
def sample_api_gateway_event():
    """Fixture com evento de exemplo do API Gateway."""
    return {
        "httpMethod": "POST",
        "path": "/sobreviventes",
        "resource": "/sobreviventes",
        "pathParameters": None,
        "queryStringParameters": None,
        "headers": {"Content-Type": "application/json"},
        "body": None,
    }
