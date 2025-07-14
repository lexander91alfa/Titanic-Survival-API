from typing import Any, Dict

from src.models.passenger_request import PassengerRequest


def map_request_to_dynamodb_item(passenger_request: PassengerRequest) -> Dict[str, Any]:
    """Maps a PassengerRequest to a DynamoDB item."""
    return {
        "passenger_id": str(passenger_request.PassengerId),
        "Pclass": passenger_request.Pclass,
        "Sex": passenger_request.Sex,
        "Age": passenger_request.Age,
        "SibSp": passenger_request.SibSp,
        "Parch": passenger_request.Parch,
        "Fare": passenger_request.Fare,
        "Embarked": passenger_request.Embarked,
    }
