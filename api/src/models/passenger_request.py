from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class PassengerRequest(BaseModel):
    """
    Modelo de dados para validar a requisição de predição de sobrevivência.
    As regras são baseadas na análise do Titanic Dataset.
    """

    PassengerId: str = Field(..., description="ID único do passageiro.", example="1")
    Pclass: int = Field(
        ..., description="Classe do ticket. Deve ser 1, 2 ou 3.", example=3
    )
    Sex: Literal["male", "female"] = Field(
        ...,
        description="Sexo do passageiro. Deve ser 'male' ou 'female'.",
        example="male",
    )
    Age: float = Field(
        ...,
        ge=0.0,
        le=120.0,
        description="Idade do passageiro em anos. Deve ser entre 0 e 120.",
        example=22.0,
    )
    SibSp: int = Field(
        ..., ge=0, description="Número de irmãos ou cônjuges a bordo.", example=1
    )
    Parch: int = Field(
        ..., ge=0, description="Número de pais ou filhos a bordo.", example=0
    )
    Fare: float = Field(
        ...,
        ge=0.0,
        description="Tarifa paga pelo passageiro. Não pode ser negativa.",
        example=7.25,
    )
    Embarked: Optional[Literal["S", "C", "Q"]] = Field(
        None,
        description="Porto de embarque: S = Southampton, C = Cherbourg, Q = Queenstown.",
        example="S",
    )

    @field_validator("Pclass")
    def pclass_must_be_in_range(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("Classe do Ticket (Pclass) deve ser 1, 2 ou 3.")
        return v

    @field_validator("Age")
    @classmethod
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError("Idade deve estar entre 0 e 120 anos.")
        return v

    @field_validator("Fare")
    @classmethod
    def validate_fare(cls, v):
        if v < 0:
            raise ValueError("Tarifa não pode ser negativa.")
        return v
