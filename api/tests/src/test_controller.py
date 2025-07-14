from src.models.passeger_request import PassengerRequest
from unittest.mock import MagicMock
import pytest


def test_create_prediction_success(passenger_controller):
    """
    Testa o fluxo de sucesso da criação de uma predição.
    Verifica se o controller chama o serviço de predição e o repositório.
    """
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

    assert response[0].get("passenger_id") == "1"
    assert response[0].get("survival_probability") == 0.3032


def test_create_prediction_multiple_passengers(passenger_controller):
    """
    Testa a criação de predições para múltiplos passageiros.
    """
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
    assert response[0].get("passenger_id") == "1"
    assert response[1].get("passenger_id") == "2"
    assert isinstance(response[0].get("survival_probability"), float)
    assert isinstance(response[1].get("survival_probability"), float)


def test_create_prediction_validation_error(passenger_controller):
    """
    Testa o tratamento de erro de validação na criação de predições.
    """
    # Mock do serviço de predição para lançar ValueError
    passenger_controller.prediction_service.predict = MagicMock(
        side_effect=ValueError("Invalid data")
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

    with pytest.raises(ValueError, match="Validation error: Invalid data"):
        passenger_controller.save_passenger(requests_data)


def test_create_prediction_unexpected_error(passenger_controller):
    """
    Testa o tratamento de erro inesperado na criação de predições.
    """
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

    with pytest.raises(Exception, match="Unexpected error: Database error"):
        passenger_controller.save_passenger(requests_data)


def test_get_all_passengers_success(passenger_controller):
    """
    Testa a recuperação bem-sucedida de todos os passageiros.
    """
    # Mock do repositório para retornar dados de teste
    mock_passengers = [
        {"passenger_id": "1", "survival_probability": 0.3032},
        {"passenger_id": "2", "survival_probability": 0.7245},
    ]
    passenger_controller.passenger_repository.get_all = MagicMock(
        return_value=mock_passengers
    )

    response = passenger_controller.get_all_passengers()

    assert len(response) == 2
    assert response[0]["passenger_id"] == "1"
    assert response[1]["passenger_id"] == "2"
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
        Exception, match="Error retrieving passengers: Database connection error"
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
        Exception, match="Error retrieving passenger with ID 1: Passenger not found"
    ):
        passenger_controller.get_passenger_by_id("1")


def test_delete_passenger_success(passenger_controller):
    """
    Testa a exclusão bem-sucedida de um passageiro.
    """
    # Mock do repositório para simular exclusão bem-sucedida
    passenger_controller.passenger_repository.delete = MagicMock()

    response = passenger_controller.delete_passenger("1")

    assert response["message"] == "Passenger with ID 1 deleted successfully."
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
        Exception, match="Error deleting passenger with ID 1: Delete operation failed"
    ):
        passenger_controller.delete_passenger("1")
