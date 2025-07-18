from src.models.passenger_request import PassengerRequest
from src.models.prediction_response import PredictionResponse
from src.models.api_response import PredictionResult, DeleteResponse
from unittest.mock import MagicMock, patch
import pytest
from decimal import Decimal


def test_create_prediction_success(passenger_controller):
    """
    Testa o fluxo de sucesso da criação de uma predição.
    Verifica se o controller chama o serviço de predição e o repositório.
    """
    # Mock the prediction service to return expected value
    with patch.object(
        passenger_controller.prediction_service, "predict", return_value=0.6631
    ):
        requests_data = [
            PassengerRequest(
                PassengerId="1",
                Pclass=3,
                Sex="male",
                Age=22.0,
                SibSp=1,
                Parch=0,
                Fare=7.25,
                Embarked="S",
            )
        ]

        response = passenger_controller.save_passenger(requests_data)

        assert len(response) == 1
        assert isinstance(response[0], PredictionResult)
        assert response[0].passenger_id == "1"
        assert response[0].survival_probability == 0.6631
        assert response[0].prediction == "survived"  # 0.6631 > 0.5
        assert response[0].confidence_level in ["low", "medium", "high"]


def test_create_prediction_multiple_passengers(passenger_controller):
    """
    Testa a criação de predições para múltiplos passageiros.
    """
    # Mock the prediction service to return different values for each passenger
    with patch.object(
        passenger_controller.prediction_service, "predict", side_effect=[0.6631, 0.8543]
    ):
        requests_data = [
            PassengerRequest(
                PassengerId="1",
                Pclass=3,
                Sex="male",
                Age=22.0,
                SibSp=1,
                Parch=0,
                Fare=7.25,
                Embarked="S",
            ),
            PassengerRequest(
                PassengerId="2",
                Pclass=1,
                Sex="female",
                Age=25.0,
                SibSp=0,
                Parch=1,
                Fare=80.0,
                Embarked="C",
            ),
        ]

        response = passenger_controller.save_passenger(requests_data)

        assert len(response) == 2
        assert isinstance(response[0], PredictionResult)
        assert isinstance(response[1], PredictionResult)
        assert response[0].passenger_id == "1"
        assert response[1].passenger_id == "2"
        assert response[0].survival_probability == 0.6631
        assert response[1].survival_probability == 0.8543
        assert response[0].prediction == "survived"
        assert response[1].prediction == "survived"


def test_create_prediction_validation_error(passenger_controller):
    """
    Testa o tratamento de erro de validação na criação de predições.
    """
    # Mock do serviço de predição para lançar ValueError
    with patch.object(
        passenger_controller.prediction_service, "predict", side_effect=ValueError("Invalid data")
    ):
        requests_data = [
            PassengerRequest(
                PassengerId="1",
                Pclass=3,
                Sex="male",
                Age=22.0,
                SibSp=1,
                Parch=0,
                Fare=7.25,
                Embarked="S",
            )
        ]

        with pytest.raises(ValueError, match="Erro de validação: Invalid data"):
            passenger_controller.save_passenger(requests_data)


def test_create_prediction_unexpected_error(passenger_controller):
    """
    Testa o tratamento de erro inesperado na criação de predições.
    """
    # Mock do serviço de predição para retornar um valor válido
    with patch.object(
        passenger_controller.prediction_service, "predict", return_value=0.75
    ):
        # Mock do repositório para lançar Exception
        passenger_controller.passenger_repository.save = MagicMock(
            side_effect=Exception("Database error")
        )

        requests_data = [
            PassengerRequest(
                PassengerId="1",
                Pclass=3,
                Sex="male",
                Age=22.0,
                SibSp=1,
                Parch=0,
                Fare=7.25,
                Embarked="S",
            )
        ]

        with pytest.raises(Exception, match="Erro inesperado: Database error"):
            passenger_controller.save_passenger(requests_data)


def test_get_all_passengers_success(passenger_controller):
    """
    Testa a recuperação bem-sucedida de todos os passageiros.
    """
    # Mock do repositório para retornar dados de teste
    mock_passengers = [
        {
            "passenger_id": "1",
            "survival_probability": 0.3032,
            "pclass": 3,
            "sex": "male",
            "age": 22,
            "sibsp": 0,
            "parch": 0,
            "fare": 7.25,
            "embarked": "S",
        },
        {
            "passenger_id": "2",
            "survival_probability": 0.7245,
            "pclass": 1,
            "sex": "female",
            "age": 28,
            "sibsp": 1,
            "parch": 0,
            "fare": 80.0,
            "embarked": "C",
        },
    ]
    passenger_controller.passenger_repository.get_all = MagicMock(
        return_value=mock_passengers
    )

    response = passenger_controller.get_all_passengers()

    assert "items" in response
    assert "pagination" in response
    assert len(response["items"]) == 2
    assert response["items"][0]["passenger_id"] == "1"
    assert response["items"][1]["passenger_id"] == "2"
    passenger_controller.passenger_repository.get_all.assert_called_once()


def test_get_all_passengers_error(passenger_controller):
    """
    Testa o tratamento de erro na recuperação de todos os passageiros.
    """
    # Mock do repositório para lançar Exception
    passenger_controller.passenger_repository.get_all = MagicMock(
        side_effect=Exception("Database connection error")
    )

    with pytest.raises(
        Exception, match="Erro ao recuperar passageiros: Database connection error"
    ):
        passenger_controller.get_all_passengers()


def test_get_passenger_by_id_success(passenger_controller):
    """
    Testa a recuperação bem-sucedida de um passageiro pelo ID.
    """
    # Mock do repositório para retornar dados de teste
    mock_passenger = {"passenger_id": "1", "survival_probability": 0.3032}
    passenger_controller.passenger_repository.get_by_id = MagicMock(
        return_value=mock_passenger
    )

    response = passenger_controller.get_passenger_by_id("1")

    assert response["passenger_id"] == "1"
    assert response["survival_probability"] == 0.3032
    passenger_controller.passenger_repository.get_by_id.assert_called_once_with("1")


def test_get_passenger_by_id_error(passenger_controller):
    """
    Testa o tratamento de erro na recuperação de um passageiro pelo ID.
    """
    # Mock do repositório para lançar Exception
    passenger_controller.passenger_repository.get_by_id = MagicMock(
        side_effect=Exception("Passenger not found")
    )

    with pytest.raises(
        Exception, match="Erro ao recuperar passageiro com ID 1: Passenger not found"
    ):
        passenger_controller.get_passenger_by_id("1")


def test_delete_passenger_success(passenger_controller):
    """
    Testa a exclusão bem-sucedida de um passageiro.
    """
    # Mock do repositório para simular exclusão bem-sucedida
    passenger_controller.passenger_repository.delete = MagicMock(return_value=True)

    response = passenger_controller.delete_passenger("1")

    assert isinstance(response, DeleteResponse)
    assert response.deleted is True
    assert response.passenger_id == "1"
    assert "excluído com sucesso" in response.message
    passenger_controller.passenger_repository.delete.assert_called_once_with("1")


def test_delete_passenger_error(passenger_controller):
    """
    Testa o tratamento de erro na exclusão de um passageiro.
    """
    # Mock do repositório para lançar Exception
    passenger_controller.passenger_repository.delete = MagicMock(
        side_effect=Exception("Delete operation failed")
    )

    with pytest.raises(
        Exception, match="Erro ao excluir passageiro com ID 1: Delete operation failed"
    ):
        passenger_controller.delete_passenger("1")


class TestPassengerControllerAdvanced:
    """Testes avançados para o PassengerController."""

    def test_save_passenger_with_decimal_conversion(self, passenger_controller):
        """Testa se os valores float são convertidos para Decimal corretamente."""
        with patch.object(
            passenger_controller.prediction_service, "predict", return_value=0.8542
        ):
            requests_data = [
                PassengerRequest(
                    PassengerId="test_decimal",
                    Pclass=1,
                    Sex="female",
                    Age=30.5,  # Float que deve ser convertido
                    SibSp=0,
                    Parch=1,
                    Fare=75.75,  # Float que deve ser convertido
                    Embarked="S",
                )
            ]

            with patch.object(
                passenger_controller.passenger_repository, "save"
            ) as mock_save:
                response = passenger_controller.save_passenger(requests_data)

                # Verificar se save foi chamado com valores Decimal
                saved_data = mock_save.call_args[0][0]
                assert isinstance(saved_data["age"], Decimal)
                assert isinstance(saved_data["fare"], Decimal)
                assert isinstance(saved_data["survival_probability"], Decimal)

                # Verificar resposta
                assert len(response) == 1
                assert response[0].passenger_id == "test_decimal"
                assert response[0].survival_probability == 0.8542

    def test_save_passenger_returns_prediction_response_objects(
        self, passenger_controller
    ):
        """Testa se save_passenger retorna objetos PredictionResponse."""
        with patch.object(
            passenger_controller.prediction_service, "predict", return_value=0.75
        ):
            requests_data = [
                PassengerRequest(
                    PassengerId="response_test",
                    Pclass=2,
                    Sex="male",
                    Age=40.0,
                    SibSp=1,
                    Parch=0,
                    Fare=25.0,
                    Embarked="Q",
                )
            ]

            response = passenger_controller.save_passenger(requests_data)

        assert len(response) == 1
        assert isinstance(response[0], PredictionResult)
        assert response[0].passenger_id == "response_test"
        assert response[0].survival_probability == 0.75

    def test_save_passenger_probability_rounding(self, passenger_controller):
        """Testa se a probabilidade é arredondada para 4 casas decimais."""
        with patch.object(
            passenger_controller.prediction_service, "predict", return_value=0.123456789
        ):
            requests_data = [
                PassengerRequest(
                    PassengerId="rounding_test",
                    Pclass=3,
                    Sex="female",
                    Age=25.0,
                    SibSp=0,
                    Parch=0,
                    Fare=10.0,
                    Embarked="S",
                )
            ]

            response = passenger_controller.save_passenger(requests_data)

            assert (
                response[0].survival_probability == 0.1235
            )  # Arredondado para 4 casas

    def test_get_all_passengers_empty_list(self, passenger_controller):
        """Testa get_all_passengers quando não há passageiros."""
        with patch.object(
            passenger_controller.passenger_repository, "get_all", return_value=[]
        ):
            result = passenger_controller.get_all_passengers()
        assert result["items"] == []
        assert result["pagination"]["total_items"] == 0

    def test_get_passenger_by_id_not_found(self, passenger_controller):
        """Testa get_passenger_by_id quando passageiro não é encontrado."""
        with patch.object(
            passenger_controller.passenger_repository, "get_by_id", return_value=None
        ):
            result = passenger_controller.get_passenger_by_id("nonexistent")
            assert result is None

    def test_delete_passenger_success_message(self, passenger_controller):
        """Testa se delete_passenger retorna mensagem de sucesso correta."""
        with patch.object(passenger_controller.passenger_repository, "delete"):
            result = passenger_controller.delete_passenger("test_id")
        expected_message = "Passageiro com ID test_id excluído com sucesso."
        assert result.message == expected_message

    def test_error_logging(self, passenger_controller):
        """Testa se erros são logados corretamente."""
        with patch.object(passenger_controller.logger, "error") as mock_log_error:
            with patch.object(
                passenger_controller.passenger_repository,
                "get_all",
                side_effect=Exception("Database connection failed"),
            ):

                with pytest.raises(Exception):
                    passenger_controller.get_all_passengers()

                mock_log_error.assert_called_once()
                assert "Database connection failed" in str(mock_log_error.call_args)
