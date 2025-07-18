import boto3
from os import getenv
from typing import Dict, Any, Optional
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
            raise ValueError(
                "Variável de ambiente DYNAMODB_TABLE_NAME não está definida."
            )
        self.table = self.dynamodb.Table(table_name)

    def save(self, passenger_data: Dict[str, Any]) -> None:
        """Salva os dados de um passageiro no DynamoDB apenas se não existir."""
        try:
            self.table.put_item(
                Item=passenger_data,
                ConditionExpression="attribute_not_exists(passenger_id)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            self.logger.warning(
                f"Passageiro {passenger_data.get('passenger_id')} já existe"
            )
            raise ValueError(
                f"Passageiro {passenger_data.get('passenger_id')} já existe"
            )
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Erro do boto3 ao salvar no DynamoDB: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro geral ao salvar no DynamoDB: {e}")
            raise

    def get_by_id(self, passenger_id: str) -> Optional[Dict[str, Any]]:
        """Busca um passageiro pelo seu ID."""
        try:
            response = self.table.get_item(Key={"passenger_id": passenger_id})
            return response.get("Item")
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Erro do boto3 ao buscar passageiro {passenger_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro geral ao buscar passageiro {passenger_id}: {e}")
            raise

    def get_all(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Retorna todos os passageiros da tabela com suporte a paginação.

        Args:
            page: Número da página (começando em 1)
            limit: Número de itens por página (padrão: 10)

        Returns:
            Dict contendo 'items', 'page', 'limit', 'total_pages' e 'count'
        """
        try:
            # Calcula quantos itens pular baseado na página
            items_to_skip = (page - 1) * limit

            scan_kwargs = {"Limit": limit}

            # Se não é a primeira página, precisa pular itens
            if items_to_skip > 0:
                # Fazer scan para pular os itens das páginas anteriores
                temp_response = self.table.scan(Limit=items_to_skip)
                if "LastEvaluatedKey" in temp_response:
                    scan_kwargs["ExclusiveStartKey"] = temp_response["LastEvaluatedKey"]
                else:
                    # Se não há mais itens, retorna lista vazia
                    return {
                        "items": [],
                        "page": page,
                        "limit": limit,
                        "total_pages": 0,
                        "count": 0,
                    }

            response = self.table.scan(**scan_kwargs)

            total_count = self.table.item_count
            total_pages = (total_count + limit - 1) // limit  # Arredonda para cima

            return {
                "items": response.get("Items", []),
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "count": response.get("Count", 0),
            }
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Erro do boto3 ao buscar todos os passageiros: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro geral ao buscar todos os passageiros: {e}")
            raise

    def delete(self, passenger_id: str) -> bool:
        """Deleta um passageiro pelo ID."""
        try:
            result = self.table.delete_item(
                Key={"passenger_id": passenger_id},
                ConditionExpression="attribute_exists(passenger_id)",
                ReturnValues="ALL_OLD",
            )
            if "Attributes" not in result:
                self.logger.warning(
                    f"Passageiro {passenger_id} não encontrado para exclusão."
                )
                return False
            return True
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            self.logger.warning(
                f"Passageiro {passenger_id} não encontrado para exclusão."
            )
            return False
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(
                f"Erro do boto3 ao deletar passageiro {passenger_id}: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Erro geral ao deletar passageiro {passenger_id}: {e}")
            raise
