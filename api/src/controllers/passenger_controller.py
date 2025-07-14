from typing import List
from src.services.predict_service import PredictionService
from src.models.passenger_request import PassengerRequest
from src.models.prediction_response import PredictionResponse
from src.repository.passenger_repository import PassengerRepository
from src.mapper.mapper import map_request_to_dynamodb_item
from src.logging.custom_logging import get_logger
from decimal import Decimal


class PassengerController:
    def __init__(self):
        self.prediction_service = PredictionService(model_name="model_fast", method="pickle")
        self.passenger_repository = PassengerRepository()
        self.logger = get_logger()

    def save_passenger(self, passengers_data: List[PassengerRequest]):
        """Saves passenger data and returns survival probability and id."""
        try:
            result = []

            self.logger.info("Iniciando o salvamento dos passageiros.")

            for passenger_request in passengers_data:
                passenger = map_request_to_dynamodb_item(passenger_request)
                survival_prob = self.prediction_service.predict(passenger)

                for key, value in passenger.items():
                    if isinstance(value, float):
                        passenger[key] = Decimal(str(value))

                passenger["survival_probability"] = Decimal(str(survival_prob))

                self.passenger_repository.save(passenger)

                response = PredictionResponse(
                    id=passenger.get("passenger_id", "desconhecido"),
                    probability=round(float(survival_prob), 4),
                )
                result.append(response)

            self.logger.info("Todos os passageiros foram salvos com sucesso.")

            return result

        except ValueError as ve:
            self.logger.error(f"Erro de validação: {str(ve)}")
            raise ValueError(f"Erro de validação: {str(ve)}")
        except Exception as e:
            self.logger.error(f"Erro inesperado: {str(e)}")
            raise Exception(f"Erro inesperado: {str(e)}")

    def get_all_passengers(self, page: int = 1, limit: int = 10):
        """Retrieves all passengers from the repository with pagination."""
        try:
            return self.passenger_repository.get_all(page=page, limit=limit)
        except Exception as e:
            self.logger.error(f"Erro ao recuperar passageiros: {str(e)}")
            raise Exception(f"Erro ao recuperar passageiros: {str(e)}")

    def get_passenger_by_id(self, passenger_id: str):
        """Retrieves a passenger by ID."""
        try:
            return self.passenger_repository.get_by_id(passenger_id)
        except Exception as e:
            self.logger.error(
                f"Erro ao recuperar passageiro com ID {passenger_id}: {str(e)}"
            )
            raise Exception(
                f"Erro ao recuperar passageiro com ID {passenger_id}: {str(e)}"
            )

    def delete_passenger(self, passenger_id: str):
        """Deletes a passenger by ID."""
        try:
            result = self.passenger_repository.delete(passenger_id)
            if result:
                return {
                    "message": f"Passageiro com ID {passenger_id} deletado com sucesso."
                }
            else:
                return {
                    "message": f"Passageiro com ID {passenger_id} não encontrado."
                }
        except Exception as e:
            self.logger.error(
                f"Erro ao deletar passageiro com ID {passenger_id}: {str(e)}"
            )
            raise Exception(
                f"Erro ao deletar passageiro com ID {passenger_id}: {str(e)}"
            )
