from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class PassengerRequest(BaseModel):
    """
    Modelo de dados para validar a requisição de predição de sobrevivência.
    As regras são baseadas na análise do Titanic Dataset.
    """

    PassengerId: Optional[int] = Field(
        None, description="ID único do passageiro.", example=1
    )
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
    def age_must_be_realistic_for_parents(cls, v, values):
        if "Parch" in values.data and values.data["Parch"] > 0 and v < 16:
            raise ValueError(
                "Um passageiro com menos de 16 anos não pode ser um pai/mãe (Parch > 0)."
            )
        return v
