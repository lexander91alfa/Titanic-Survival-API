# Em um novo arquivo, ex: src/repositories/passenger_repository.py
import boto3
from typing import Dict, Any, List, Optional

class PassengerRepository:
    """
    Classe responsável por toda a comunicação com a tabela
    de passageiros no DynamoDB.
    """
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save(self, passenger_data: Dict[str, Any]) -> None:
        """Salva os dados de um passageiro no DynamoDB."""
        try:
            self.table.put_item(Item=passenger_data)
        except Exception as e:
            # Adicione logging de erro aqui
            print(f"Erro ao salvar no DynamoDB: {e}")
            raise  # Re-lança a exceção para o serviço tratar

    def get_by_id(self, passenger_id: str) -> Optional[Dict[str, Any]]:
        """Busca um passageiro pelo seu ID."""
        response = self.table.get_item(Key={'id': passenger_id})
        return response.get('Item')

    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os passageiros da tabela."""
        response = self.table.scan()
        return response.get('Items', [])
        
    def delete(self, passenger_id: str) -> bool:
        """Deleta um passageiro pelo ID."""
        self.table.delete_item(Key={'id': passenger_id})
        return True