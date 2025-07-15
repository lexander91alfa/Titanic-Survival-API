from typing import Any, Dict
from decimal import Decimal
from pytz import timezone
from datetime import datetime

timezone_sao_paulo = timezone("America/Sao_Paulo")

from src.models.passenger_request import PassengerRequest


def map_request_to_dynamodb_item(passenger_request: PassengerRequest) -> Dict[str, Any]:
    """Maps a PassengerRequest to a DynamoDB item."""
    return {
        "passenger_id": str(passenger_request.PassengerId),
        "pclass": int(passenger_request.Pclass),
        "sex": passenger_request.Sex,
        "age": Decimal(passenger_request.Age).quantize(Decimal("1.00")),
        "sibsp": int(passenger_request.SibSp),
        "parch": int(passenger_request.Parch),
        "fare": Decimal(passenger_request.Fare).quantize(Decimal("1.00")),
        "embarked": passenger_request.Embarked,
        "created_at": datetime.now(timezone_sao_paulo).isoformat(),
    }
