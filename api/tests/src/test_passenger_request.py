import pytest
from pydantic import ValidationError
from src.models.passenger_request import PassengerRequest


class TestPassengerRequest:
    """Testes para o modelo PassengerRequest."""

    def test_valid_passenger_request(self):
        """Testa criação de uma requisição válida."""
        passenger_data = {
            "PassengerId": "1",
            "Pclass": 3,
            "Sex": "male",
            "Age": 22.0,
            "SibSp": 1,
            "Parch": 0,
            "Fare": 7.25,
            "Embarked": "S",
        }

        passenger = PassengerRequest(**passenger_data)

        assert passenger.PassengerId == "1"
        assert passenger.Pclass == 3
        assert passenger.Sex == "male"
        assert passenger.Age == 22.0
        assert passenger.SibSp == 1
        assert passenger.Parch == 0
        assert passenger.Fare == 7.25
        assert passenger.Embarked == "S"

    def test_passenger_request_without_embarked(self):
        """Testa criação de requisição sem embarked (campo opcional)."""
        passenger_data = {
            "PassengerId": "2",
            "Pclass": 1,
            "Sex": "female",
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 1,
            "Fare": 50.0,
        }

        passenger = PassengerRequest(**passenger_data)
        assert passenger.Embarked is None

    def test_invalid_pclass_value(self):
        """Testa validação de Pclass com valor inválido."""
        passenger_data = {
            "PassengerId": "3",
            "Pclass": 4,  # Inválido
            "Sex": "male",
            "Age": 30.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 10.0,
            "Embarked": "S",
        }

        with pytest.raises(ValidationError) as exc_info:
            PassengerRequest(**passenger_data)

        errors = exc_info.value.errors()
        assert any(
            "Classe do Ticket (Pclass) deve ser 1, 2 ou 3" in str(error)
            for error in errors
        )

    def test_invalid_sex_value(self):
        """Testa validação de Sex com valor inválido."""
        passenger_data = {
            "PassengerId": "4",
            "Pclass": 2,
            "Sex": "other",  # Inválido
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 15.0,
            "Embarked": "C",
        }

        with pytest.raises(ValidationError):
            PassengerRequest(**passenger_data)

    def test_negative_age(self):
        """Testa validação de idade negativa."""
        passenger_data = {
            "PassengerId": "5",
            "Pclass": 1,
            "Sex": "female",
            "Age": -5.0,  # Inválido
            "SibSp": 0,
            "Parch": 0,
            "Fare": 100.0,
            "Embarked": "Q",
        }

        with pytest.raises(ValidationError) as exc_info:
            PassengerRequest(**passenger_data)

        errors = exc_info.value.errors()
        # Verifica se há erro relacionado à idade
        assert any(error.get("loc") == ("Age",) for error in errors)

    def test_age_over_limit(self):
        """Testa validação de idade acima do limite."""
        passenger_data = {
            "PassengerId": "6",
            "Pclass": 2,
            "Sex": "male",
            "Age": 150.0,  # Inválido
            "SibSp": 0,
            "Parch": 0,
            "Fare": 25.0,
            "Embarked": "S",
        }

        with pytest.raises(ValidationError) as exc_info:
            PassengerRequest(**passenger_data)

        errors = exc_info.value.errors()
        # Verifica se há erro relacionado à idade
        assert any(error.get("loc") == ("Age",) for error in errors)

    def test_negative_sibsp(self):
        """Testa validação de SibSp negativo."""
        passenger_data = {
            "PassengerId": "7",
            "Pclass": 3,
            "Sex": "male",
            "Age": 30.0,
            "SibSp": -1,  # Inválido
            "Parch": 0,
            "Fare": 8.0,
            "Embarked": "S",
        }

        with pytest.raises(ValidationError):
            PassengerRequest(**passenger_data)

    def test_negative_parch(self):
        """Testa validação de Parch negativo."""
        passenger_data = {
            "PassengerId": "8",
            "Pclass": 1,
            "Sex": "female",
            "Age": 35.0,
            "SibSp": 1,
            "Parch": -1,  # Inválido
            "Fare": 75.0,
            "Embarked": "C",
        }

        with pytest.raises(ValidationError):
            PassengerRequest(**passenger_data)

    def test_negative_fare(self):
        """Testa validação de Fare negativo."""
        passenger_data = {
            "PassengerId": "9",
            "Pclass": 2,
            "Sex": "male",
            "Age": 28.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": -10.0,  # Inválido
            "Embarked": "Q",
        }

        with pytest.raises(ValidationError) as exc_info:
            PassengerRequest(**passenger_data)

        errors = exc_info.value.errors()
        # Verifica se há erro relacionado à tarifa
        assert any(error.get("loc") == ("Fare",) for error in errors)

    def test_invalid_embarked_value(self):
        """Testa validação de Embarked com valor inválido."""
        passenger_data = {
            "PassengerId": "10",
            "Pclass": 3,
            "Sex": "female",
            "Age": 22.0,
            "SibSp": 0,
            "Parch": 1,
            "Fare": 12.0,
            "Embarked": "X",  # Inválido
        }

        with pytest.raises(ValidationError):
            PassengerRequest(**passenger_data)

    def test_missing_required_fields(self):
        """Testa validação quando campos obrigatórios estão ausentes."""
        passenger_data = {
            "PassengerId": "11",
            # Pclass ausente
            "Sex": "male",
            "Age": 25.0,
            # SibSp ausente
            "Parch": 0,
            "Fare": 20.0,
        }

        with pytest.raises(ValidationError):
            PassengerRequest(**passenger_data)

    def test_boundary_age_values(self):
        """Testa valores limite para idade."""
        # Idade mínima
        passenger_data_min = {
            "PassengerId": "12",
            "Pclass": 1,
            "Sex": "female",
            "Age": 0.0,
            "SibSp": 0,
            "Parch": 2,
            "Fare": 100.0,
            "Embarked": "S",
        }

        passenger_min = PassengerRequest(**passenger_data_min)
        assert passenger_min.Age == 0.0

        # Idade máxima
        passenger_data_max = {
            "PassengerId": "13",
            "Pclass": 2,
            "Sex": "male",
            "Age": 120.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 50.0,
            "Embarked": "C",
        }

        passenger_max = PassengerRequest(**passenger_data_max)
        assert passenger_max.Age == 120.0
