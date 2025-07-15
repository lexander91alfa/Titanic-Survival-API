import json
import uuid
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
from src.models.api_response import StandardSuccessResponse, APIMetadata, HealthResponse
from src.models.error_response import StandardErrorResponse


class HTTPAdapter:
    """
    Adapta o evento do API Gateway para uma interface mais simples e
    formata as respostas de volta para o formato esperado pela AWS.
    """

    def __init__(self, event: Dict[str, Any]):
        self._event = event
        self._body = None  # Cache para o corpo decodificado
        self._request_id = str(uuid.uuid4())  # Gerar ID único para a requisição

    @property
    def request_id(self) -> str:
        """Retorna o ID único da requisição."""
        return self._request_id

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
    def resource(self) -> Optional[str]:
        """Retorna o recurso da requisição."""
        return self._event.get("resource")

    @property
    def headers(self) -> Dict[str, str]:
        """Retorna os cabeçalhos da requisição."""
        return self._event.get("headers") or {}

    @property
    def query_parameters(self) -> Dict[str, str]:
        """Retorna os parâmetros de consulta (query) como um dicionário."""
        return self._event.get("queryStringParameters") or {}

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
        Método estático para construir a resposta HTTP (formato legacy).
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
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(body_content, ensure_ascii=False, default=str) if body_content is not None else None
        }

    @staticmethod
    def build_standard_response(
        status_code: int, 
        body_data: Any, 
        request_id: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Método estático para construir a resposta HTTP padronizada.
        Converte modelos Pydantic para dicionários automaticamente.
        """
        # Se for um erro, manter o formato atual
        if isinstance(body_data, StandardErrorResponse):
            body_content = body_data.model_dump()
        elif isinstance(body_data, HealthResponse):
            # Health check tem formato próprio, não envolver em StandardSuccessResponse
            body_content = body_data.model_dump()
        elif isinstance(body_data, dict) and body_data.get("error") is True:
            # Manter formato de erro existente
            body_content = body_data
        elif status_code >= 400:
            # Para erros que não são StandardErrorResponse
            if isinstance(body_data, BaseModel):
                body_content = body_data.model_dump()
            else:
                body_content = body_data
        else:
            # Para sucessos, usar StandardSuccessResponse
            metadata = APIMetadata()
            if request_id:
                metadata.request_id = request_id
            
            # Determinar mensagem padrão baseada no status
            if not message:
                if status_code == 200:
                    message = "Operação realizada com sucesso"
                elif status_code == 201:
                    message = "Recurso criado com sucesso"
                elif status_code == 204:
                    message = "Operação realizada com sucesso"
                else:
                    message = "Operação concluída"
            
            # Converter body_data para dict se for um modelo Pydantic
            if isinstance(body_data, BaseModel):
                data = body_data.model_dump()
            else:
                data = body_data
            
            success_response = StandardSuccessResponse(
                message=message,
                data=data,
                metadata=metadata
            )
            body_content = success_response.model_dump()

        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                "X-Request-ID": request_id or str(uuid.uuid4()),
            },
            "body": json.dumps(body_content, ensure_ascii=False, default=str)
        }
