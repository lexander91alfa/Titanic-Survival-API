from pydantic import BaseModel, Field
from typing import Dict, Any


class PredictionResponse(BaseModel):
    id: str = Field(..., description="ID único da predição")
    probability: float = Field(
        ..., description="Probabilidade de sobrevivência (0.0 a 1.0)"
    )


class PassengerDetailsResponse(BaseModel):
    id: str
    probability: str
    input_data: Dict[str, Any]
