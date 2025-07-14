import json
from prediction_handler import lambda_handler


def test_handler_post_success(passenger_repository):
    """
    Testa o handler da Lambda com um evento POST válido, mockando as dependências.
    """

    test_event = {
        "httpMethod": "POST",
        "path": "/sobreviventes",
        "body": json.dumps(
            {
                "PassengerId": "1",
                "Pclass": 1,
                "Sex": "female",
                "Age": 38.0,
                "SibSp": 1,
                "Parch": 0,
                "Fare": 71.2833,
                "Embarked": "C",
            }
        ),
    }

    response = lambda_handler(test_event, None)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert "PassengerId" in body
    assert body["probability"] == 0.7316


def test_handler_validation_error(passenger_repository):
    """
    Testa se o handler retorna um erro 422 para uma requisição com dados inválidos.
    """

    test_event = {
        "httpMethod": "POST",
        "path": "/sobreviventes",
        "body": json.dumps({"Pclass": 99, "Sex": "alien", "Age": -10}),
    }

    response = lambda_handler(test_event, None)

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert "detail" in body
    assert "Validation Error" in body["detail"]
    assert len(body["errors"]) > 0
