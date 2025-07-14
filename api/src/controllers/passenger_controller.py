from typing import List
from src.services.predict_service import PredictionService
from src.models.passeger_request import PassengerRequest
from src.models.prediction_response import PredictionResponse
from src.repository.passenger_repository import PassengerRepository
from src.mapper.mapper import map_request_to_dynamodb_item
from src.logging.custom_logging import get_logger
from decimal import Decimal


class PassengerController:
    def __init__(self):
        self.prediction_service = PredictionService(model_name="model")
        self.passenger_repository = PassengerRepository()
        self.logger = get_logger()

    def save_passenger(self, passengers_data: List[PassengerRequest]):
        """Saves passenger data and returns survival probability and id."""
        try:
            result = []

            for passenger_request in passengers_data:
                passenger = map_request_to_dynamodb_item(passenger_request)
                survival_prob = self.prediction_service.predict(passenger)

                for key, value in passenger.items():
                    if isinstance(value, float):
                        passenger[key] = Decimal(str(value))

                passenger["survival_probability"] = Decimal(str(survival_prob))

                self.passenger_repository.save(passenger)

                response = PredictionResponse(
                    id=passenger.get("passenger_id", "unknown"),
                    probability=round(float(survival_prob), 4)
                )
                result.append(response)

            return result

        except ValueError as ve:
            self.logger.error(f"Validation error: {str(ve)}")
            raise ValueError(f"Validation error: {str(ve)}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")

    def get_all_passengers(self):
        """Retrieves all passengers from the repository."""
        try:
            return self.passenger_repository.get_all()
        except Exception as e:
            self.logger.error(f"Error retrieving passengers: {str(e)}")
            raise Exception(f"Error retrieving passengers: {str(e)}")

    def get_passenger_by_id(self, passenger_id: str):
        """Retrieves a passenger by ID."""
        try:
            return self.passenger_repository.get_by_id(passenger_id)
        except Exception as e:
            self.logger.error(
                f"Error retrieving passenger with ID {passenger_id}: {str(e)}"
            )
            raise Exception(
                f"Error retrieving passenger with ID {passenger_id}: {str(e)}"
            )

    def delete_passenger(self, passenger_id: str):
        """Deletes a passenger by ID."""
        try:
            self.passenger_repository.delete(passenger_id)
            return {
                "message": f"Passenger with ID {passenger_id} deleted successfully."
            }
        except Exception as e:
            self.logger.error(
                f"Error deleting passenger with ID {passenger_id}: {str(e)}"
            )
            raise Exception(
                f"Error deleting passenger with ID {passenger_id}: {str(e)}"
            )
