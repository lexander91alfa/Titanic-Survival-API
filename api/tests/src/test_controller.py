from src.models.passeger_request import PassengerRequest
from unittest.mock import MagicMock

def test_create_prediction_success(passenger_controller):
    """
    Testa o fluxo de sucesso da criação de uma predição.
    Verifica se o controller chama o serviço de predição e o repositório.
    """
    requests_data = [
        PassengerRequest(
            PassengerId="1", Pclass=3, Sex="male", Age=22.0, SibSp=1, Parch=0, Fare=7.25, Embarked="S"
        )
    ]

    response = passenger_controller.save_passenger(requests_data)

    assert response.id == "1"
    assert response.probability == 0.85