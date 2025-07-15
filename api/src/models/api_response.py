from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from pytz import timezone

timezone_sao_paulo = timezone("America/Sao_Paulo")


class APIMetadata(BaseModel):
    """Metadados da resposta da API."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone_sao_paulo).isoformat() + "Z")
    version: str = Field(default="1.0.0", description="Versão da API")
    request_id: Optional[str] = Field(None, description="ID único da requisição")


class PaginationInfo(BaseModel):
    """Informações de paginação."""
    page: int = Field(..., ge=1, description="Página atual")
    limit: int = Field(..., ge=1, le=100, description="Itens por página")
    total_items: int = Field(..., ge=0, description="Total de itens")
    total_pages: int = Field(..., ge=0, description="Total de páginas")
    has_next: bool = Field(..., description="Indica se há próxima página")
    has_previous: bool = Field(..., description="Indica se há página anterior")


class StandardSuccessResponse(BaseModel):
    """Resposta de sucesso padronizada da API."""
    success: bool = Field(True, description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de sucesso")
    data: Optional[Any] = Field(None, description="Dados da resposta")
    pagination: Optional[PaginationInfo] = Field(None, description="Informações de paginação")
    metadata: APIMetadata = Field(default_factory=APIMetadata)


class PredictionResult(BaseModel):
    """Resultado de uma predição de sobrevivência."""
    passenger_id: str = Field(..., description="ID único do passageiro")
    survival_probability: float = Field(..., ge=0.0, le=1.0, description="Probabilidade de sobrevivência (0.0 a 1.0)")
    prediction: str = Field(..., description="Predição categórica (survived/not_survived)")
    confidence_level: str = Field(..., description="Nível de confiança da predição")
    
    @classmethod
    def from_probability(cls, passenger_id: str, probability: float) -> "PredictionResult":
        """Cria um resultado de predição a partir da probabilidade."""
        prediction = "survived" if probability >= 0.5 else "not_survived"
        
        # Determinar nível de confiança
        if probability >= 0.8 or probability <= 0.2:
            confidence = "high"
        elif probability >= 0.65 or probability <= 0.35:
            confidence = "medium"
        else:
            confidence = "low"
            
        return cls(
            passenger_id=passenger_id,
            survival_probability=round(probability, 4),
            prediction=prediction,
            confidence_level=confidence
        )


class PassengerDetail(BaseModel):
    """Detalhes completos de um passageiro."""
    passenger_id: str = Field(..., description="ID único do passageiro")
    survival_probability: float = Field(..., description="Probabilidade de sobrevivência")
    prediction: str = Field(..., description="Predição categórica")
    confidence_level: str = Field(..., description="Nível de confiança")
    passenger_class: int = Field(..., description="Classe do passageiro")
    sex: str = Field(..., description="Sexo do passageiro")
    age: Optional[float] = Field(None, description="Idade do passageiro")
    siblings_spouses: int = Field(..., description="Número de irmãos/cônjuges a bordo")
    parents_children: int = Field(..., description="Número de pais/filhos a bordo")
    fare: Optional[float] = Field(None, description="Tarifa paga")
    embarked: Optional[str] = Field(None, description="Porto de embarque")
    created_at: Optional[str] = Field(None, description="Data de criação do registro")


class HealthStatus(BaseModel):
    """Status de saúde de um componente."""
    status: str = Field(..., description="Status do componente (healthy/unhealthy)")
    message: str = Field(..., description="Mensagem sobre o status")
    last_check: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class HealthResponse(BaseModel):
    """Resposta do health check."""
    overall_status: str = Field(..., description="Status geral do serviço")
    components: Dict[str, HealthStatus] = Field(..., description="Status dos componentes")
    uptime: Optional[str] = Field(None, description="Tempo de atividade do serviço")
    metadata: APIMetadata = Field(default_factory=APIMetadata)


class DeleteResponse(BaseModel):
    """Resposta para operações de exclusão."""
    deleted: bool = Field(..., description="Indica se o item foi excluído")
    passenger_id: str = Field(..., description="ID do passageiro excluído")
    message: str = Field(..., description="Mensagem sobre a operação")
