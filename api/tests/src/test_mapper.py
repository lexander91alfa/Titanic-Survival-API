import pytest
from src.mapper.mapper import map_request_to_dynamodb_item
from src.models.passenger_request import PassengerRequest
from decimal import Decimal


class TestMapper:
    """Testes para a função map_request_to_dynamodb_item."""

    def test_map_passenger_id_conversion_to_string(self):
        """Testa se PassengerId é convertido para string."""
        passenger_request = PassengerRequest(
            PassengerId="789",
            Pclass=2,
            Sex="female",
            Age=35.5,
            SibSp=1,
            Parch=1,
            Fare=50.0,
            Embarked="C",
        )

        result = map_request_to_dynamodb_item(passenger_request)

        assert result["passenger_id"] == "789"
        assert isinstance(result["passenger_id"], str)

    def test_map_all_passenger_classes(self):
        """Testa mapeamento para todas as classes de passageiro."""
        test_cases = [(1, "first_class"), (2, "second_class"), (3, "third_class")]

        for pclass, test_id in test_cases:
            passenger_request = PassengerRequest(
                PassengerId=test_id,
                Pclass=pclass,
                Sex="female",
                Age=25.0,
                SibSp=0,
                Parch=0,
                Fare=50.0,
                Embarked="S",
            )

            result = map_request_to_dynamodb_item(passenger_request)
            assert result["pclass"] == pclass

    def test_map_all_sex_values(self):
        """Testa mapeamento para ambos os sexos."""
        test_cases = [("male", "male_passenger"), ("female", "female_passenger")]

        for sex, test_id in test_cases:
            passenger_request = PassengerRequest(
                PassengerId=test_id,
                Pclass=1,
                Sex=sex,
                Age=30.0,
                SibSp=0,
                Parch=0,
                Fare=75.0,
                Embarked="Q",
            )

            result = map_request_to_dynamodb_item(passenger_request)
            assert result["sex"] == sex

    def test_map_all_embarked_values(self):
        """Testa mapeamento para todos os portos de embarque."""
        test_cases = [("S", "southampton"), ("C", "cherbourg"), ("Q", "queenstown")]

        for embarked, test_id in test_cases:
            passenger_request = PassengerRequest(
                PassengerId=test_id,
                Pclass=2,
                Sex="male",
                Age=40.0,
                SibSp=1,
                Parch=0,
                Fare=25.0,
                Embarked=embarked,
            )

            result = map_request_to_dynamodb_item(passenger_request)
            assert result["embarked"] == embarked

    def test_map_boundary_values(self):
        """Testa mapeamento com valores limite."""
        passenger_request = PassengerRequest(
            PassengerId="boundary_test",
            Pclass=3,
            Sex="male",
            Age=0.0,  # Idade mínima
            SibSp=0,  # Mínimo SibSp
            Parch=0,  # Mínimo Parch
            Fare=0.0,  # Tarifa mínima
            Embarked="S",
        )

        result = map_request_to_dynamodb_item(passenger_request)

        assert result["age"] == 0.0
        assert result["sibsp"] == 0
        assert result["parch"] == 0
        assert result["fare"] == 0.0

    def test_map_high_values(self):
        """Testa mapeamento com valores altos."""
        passenger_request = PassengerRequest(
            PassengerId="high_values_test",
            Pclass=1,
            Sex="female",
            Age=120.0,  # Idade máxima
            SibSp=8,  # Alto número de irmãos/cônjuges
            Parch=6,  # Alto número de pais/filhos
            Fare=500.0,  # Tarifa alta
            Embarked="C",
        )

        result = map_request_to_dynamodb_item(passenger_request)

        assert result["age"] == 120.0
        assert result["sibsp"] == 8
        assert result["parch"] == 6
        assert result["fare"] == 500.0

    def test_map_preserves_data_types(self):
        """Testa se os tipos de dados são preservados no mapeamento."""
        passenger_request = PassengerRequest(
            PassengerId="type_test",
            Pclass=2,
            Sex="male",
            Age=45.5,
            SibSp=2,
            Parch=1,
            Fare=88.75,
            Embarked="Q",
        )

        result = map_request_to_dynamodb_item(passenger_request)

        # Verificar tipos
        assert isinstance(result["passenger_id"], str)
        assert isinstance(result["pclass"], int)
        assert isinstance(result["sex"], str)
        assert isinstance(result["age"], Decimal)
        assert isinstance(result["sibsp"], int)
        assert isinstance(result["parch"], int)
        assert isinstance(result["fare"], Decimal)
        assert isinstance(result["embarked"], str)

    def test_map_contains_all_required_fields(self):
        """Testa se o mapeamento contém todos os campos necessários."""
        passenger_request = PassengerRequest(
            PassengerId="fields_test",
            Pclass=1,
            Sex="female",
            Age=28.0,
            SibSp=0,
            Parch=1,
            Fare=120.0,
            Embarked="S",
        )

        result = map_request_to_dynamodb_item(passenger_request)

        expected_fields = [
            "passenger_id",
            "pclass",
            "sex",
            "age",
            "sibsp",
            "parch",
            "fare",
            "embarked",
            "created_at"
        ]

        for field in expected_fields:
            assert field in result

        assert len(result) == len(expected_fields)
