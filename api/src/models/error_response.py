from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Detalhes específicos de um erro de validação."""
    field: str
    message: str
    type: str


class StandardErrorResponse(BaseModel):
    """Resposta de erro padronizada para a API."""
    error: bool = True
    message: str
    details: Optional[List[ErrorDetail]] = None
    status_code: int

    @classmethod
    def validation_error(cls, errors: List[Dict[str, Any]]) -> "StandardErrorResponse":
        """Cria uma resposta de erro para erros de validação."""
        error_details = []
        for error in errors:
            error_details.append(ErrorDetail(
                field=error.get("loc", ["unknown"])[0] if error.get("loc") else "unknown",
                message=error.get("msg", "Validation error"),
                type=error.get("type", "unknown")
            ))
        
        return cls(
            message="Erro de validação nos dados fornecidos",
            details=error_details,
            status_code=422
        )

    @classmethod
    def business_error(cls, message: str, status_code: int = 400) -> "StandardErrorResponse":
        """Cria uma resposta de erro para erros de negócio."""
        return cls(
            message=message,
            status_code=status_code
        )

    @classmethod
    def internal_error(cls, message: str = "Erro interno do servidor") -> "StandardErrorResponse":
        """Cria uma resposta de erro para erros internos."""
        return cls(
            message=message,
            status_code=500
        )
