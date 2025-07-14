from pytest import fixture
import os
import boto3
from moto import mock_aws
from unittest.mock import MagicMock
import os

from src.repository.passenger_repository import PassengerRepository
from src.services.predict_service import PredictionService
from src.controllers.passenger_controller import PassengerController

@fixture(scope="session", autouse=True)
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
            KeySchema=[{'AttributeName': 'passenger_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'passenger_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
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