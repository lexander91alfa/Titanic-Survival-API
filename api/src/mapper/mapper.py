from typing import Any, Dict

from src.models.passeger_request import PassengerRequest


def map_request_to_dynamodb_item(passenger_request: PassengerRequest) -> Dict[str, Any]:
    """Maps a PassengerRequest to a DynamoDB item."""
    return {
        "passenger_id": str(passenger_request.PassengerId),
        "pclass": passenger_request.Pclass,
        "sex": passenger_request.Sex,
        "age": passenger_request.Age,
        "sibsp": passenger_request.SibSp,
        "parch": passenger_request.Parch,
        "fare": passenger_request.Fare,
        "embarked": passenger_request.Embarked,
    }
