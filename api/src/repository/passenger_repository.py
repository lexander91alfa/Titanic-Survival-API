import boto3
from os import getenv
from typing import Dict, Any, List, Optional
from src.logging.custom_logging import get_logger


class PassengerRepository:
    """
    Classe responsável por toda a comunicação com a tabela
    de passageiros no DynamoDB.
    """

    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.logger = get_logger()
        table_name = getenv("DYNAMODB_TABLE_NAME")
        if not table_name:
            raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set.")
        self.table = self.dynamodb.Table(table_name)

    def save(self, passenger_data: Dict[str, Any]) -> None:
        """Salva os dados de um passageiro no DynamoDB."""
        try:
            self.table.put_item(Item=passenger_data)
        except Exception as e:
            self.logger.error(f"Erro ao salvar no DynamoDB: {e}")
            raise

    def get_by_id(self, passenger_id: str) -> Optional[Dict[str, Any]]:
        """Busca um passageiro pelo seu ID."""
        response = self.table.get_item(Key={"passenger_id": passenger_id})
        return response.get("Item")

    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os passageiros da tabela."""
        response = self.table.scan()
        return response.get("Items", [])

    def delete(self, passenger_id: str) -> bool:
        """Deleta um passageiro pelo ID."""
        self.table.delete_item(Key={"passenger_id": passenger_id})
        return True
