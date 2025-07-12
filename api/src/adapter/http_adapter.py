import json
from typing import Dict, Any, Optional
from pydantic import BaseModel


class HTTPAdapter:
    """
    Adapta o evento do API Gateway para uma interface mais simples e
    formata as respostas de volta para o formato esperado pela AWS.
    """

    def __init__(self, event: Dict[str, Any]):
        self._event = event
        self._body = None  # Cache para o corpo decodificado

    @property
    def method(self) -> Optional[str]:
        """Retorna o método HTTP da requisição."""
        return self._event.get("httpMethod")

    @property
    def path(self) -> Optional[str]:
        """Retorna o caminho (path) da requisição."""
        return self._event.get("path")

    @property
    def path_parameters(self) -> Dict[str, str]:
        """Retorna os parâmetros do caminho como um dicionário."""
        return self._event.get("pathParameters") or {}

    @property
    def body(self) -> Any:
        """
        Retorna o corpo (body) da requisição, já decodificado de JSON.
        Retorna um dicionário vazio se o corpo for nulo ou vazio.
        """
        if self._body is None:
            raw_body = self._event.get("body")
            if raw_body:
                try:
                    self._body = json.loads(raw_body)
                except json.JSONDecodeError:
                    self._body = {}  # Ou poderia levantar um erro aqui
            else:
                self._body = {}
        return self._body

    @staticmethod
    def build_response(status_code: int, body_data: Any) -> Dict[str, Any]:
        """
        Método estático para construir a resposta HTTP.
        Converte modelos Pydantic para dicionários automaticamente.
        """
        if isinstance(body_data, BaseModel):
            body_content = body_data.model_dump()
        else:
            body_content = body_data

        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Boa prática para CORS
            },
            "body": json.dumps(body_content),
        }
