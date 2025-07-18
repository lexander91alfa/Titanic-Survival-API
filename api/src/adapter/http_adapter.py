import json
import uuid
from typing import Dict, Any, Optional

from pydantic import BaseModel
from src.models.api_response import StandardSuccessResponse, APIMetadata, HealthResponse
from src.models.error_response import StandardErrorResponse


class HTTPAdapter:
    """
    Adapta o evento do API Gateway v1.0 (REST API) para uma interface mais simples e
    formata as respostas de volta para o formato esperado pela AWS.
    """

    def __init__(self, event: Dict[str, Any]):
        self._event = event
        self._body = None  # Cache para o corpo decodificado
        self._request_id = self._event.get("requestContext", {}).get(
            "requestId", str(uuid.uuid4())
        )

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
                if self._event.get("isBase64Encoded", False):
                    import base64

                    try:
                        raw_body = base64.b64decode(raw_body).decode("utf-8")
                    except Exception:
                        self._body = {}
                        return self._body

                try:
                    # O corpo pode já ser um dict se não for base64, mas a conversão é segura
                    self._body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
                except (json.JSONDecodeError, TypeError):
                    self._body = {}
            else:
                self._body = {}
        return self._body

    @property
    def stage(self) -> Optional[str]:
        """Retorna o stage da API."""
        return self._event.get("requestContext", {}).get("stage")

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
            "body": (
                json.dumps(body_content, ensure_ascii=False, default=str)
                if body_content is not None
                else None
            ),
        }

    @staticmethod
    def build_standard_response(
        status_code: int,
        body_data: Any,
        request_id: Optional[str] = None,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Método estático para construir a resposta HTTP padronizada para API Gateway.
        Converte modelos Pydantic para dicionários automaticamente.
        """
        body_content = {}
        if isinstance(body_data, (StandardErrorResponse, HealthResponse)):
            body_content = body_data.model_dump()
        elif isinstance(body_data, dict) and body_data.get("error") is True:
            body_content = body_data
        elif status_code >= 400:
            body_content = body_data.model_dump() if isinstance(body_data, BaseModel) else body_data
        else:
            metadata = APIMetadata(request_id=request_id or str(uuid.uuid4()))
            
            if not message:
                message_map = {
                    200: "Operação realizada com sucesso",
                    201: "Recurso criado com sucesso",
                    204: "Operação realizada com sucesso",
                }
                message = message_map.get(status_code, "Operação concluída")

            data = body_data.model_dump() if isinstance(body_data, BaseModel) else body_data

            success_response = StandardSuccessResponse(
                message=message, data=data, metadata=metadata
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
            "body": json.dumps(body_content, ensure_ascii=False, default=str),
        }
