from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class PassengerRequest(BaseModel):
    """
    Modelo de dados para validar a requisição de predição de sobrevivência.
    As regras são baseadas na análise do Titanic Dataset.
    """

    PassengerId: str = Field(
        ..., description="ID único do passageiro.", json_schema_extra={"example": "1"}
    )
    Pclass: int = Field(
        ...,
        description="Classe do ticket. Deve ser 1, 2 ou 3.",
        json_schema_extra={"example": 3},
    )
    Sex: Literal["male", "female"] = Field(
        ...,
        description="Sexo do passageiro. Deve ser 'male' ou 'female'.",
        json_schema_extra={"example": "male"},
    )
    Age: float = Field(
        ...,
        ge=0.0,
        le=120.0,
        description="Idade do passageiro em anos. Deve ser entre 0 e 120.",
        json_schema_extra={"example": 22.0},
    )
    SibSp: int = Field(
        ...,
        ge=0,
        description="Número de irmãos ou cônjuges a bordo.",
        json_schema_extra={"example": 1},
    )
    Parch: int = Field(
        ...,
        ge=0,
        description="Número de pais ou filhos a bordo.",
        json_schema_extra={"example": 0},
    )
    Fare: float = Field(
        ...,
        ge=0.0,
        description="Tarifa paga pelo passageiro. Não pode ser negativa.",
        json_schema_extra={"example": 7.25},
    )
    Embarked: Optional[Literal["S", "C", "Q"]] = Field(
        None,
        description="Porto de embarque: S = Southampton, C = Cherbourg, Q = Queenstown.",
        json_schema_extra={"example": "S"},
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

    @classmethod
    def from_dict(cls, data: dict) -> "PassengerRequest":
        """
        Cria uma instância de PassengerRequest a partir de um dicionário.
        """
        return cls(
            PassengerId=str(data["PassengerId"]),
            Pclass=int(data["Pclass"]),
            Sex=data["Sex"],
            Age=float(data["Age"]),
            SibSp=int(data["SibSp"]),
            Parch=int(data["Parch"]),
            Fare=float(data["Fare"]),
            Embarked=data.get("Embarked"),
        )

    def to_dict(self) -> dict:
        """
        Converte a instância atual em um dicionário.
        """
        return {
            "PassengerId": self.PassengerId,
            "Pclass": self.Pclass,
            "Sex": self.Sex,
            "Age": self.Age,
            "SibSp": self.SibSp,
            "Parch": self.Parch,
            "Fare": self.Fare,
            "Embarked": self.Embarked,
        }
