from typing import List, Dict, Any
from src.services.predict_service import PredictionService
from src.models.passenger_request import PassengerRequest
from src.models.prediction_response import PredictionResponse
from src.models.api_response import (
    PredictionResult,
    PassengerDetail,
    DeleteResponse,
    PaginationInfo,
)
from src.repository.passenger_repository import PassengerRepository
from src.mapper.mapper import map_request_to_dynamodb_item
from src.logging.custom_logging import get_logger
from decimal import Decimal
import math


class PassengerController:
    def __init__(self):
        self.prediction_service = PredictionService(model_name="model.joblib", method="joblib")
        self.passenger_repository = PassengerRepository()
        self.logger = get_logger()

    def save_passenger(
        self, passengers_data: List[PassengerRequest]
    ) -> List[PredictionResult]:
        """Salva os dados do passageiro e retorna a predição de sobrevivência estruturada."""
        try:
            result = []

            self.logger.info("Iniciando o salvamento dos passageiros.")

            for passenger_request in passengers_data:
                passenger = map_request_to_dynamodb_item(passenger_request)
                survival_prob = self.prediction_service.predict(passenger)

                passenger["survival_probability"] = Decimal(str(survival_prob))

                self.passenger_repository.save(passenger)

                prediction_result = PredictionResult.from_probability(
                    passenger_id=passenger.get("passenger_id", "unknown"),
                    probability=float(survival_prob),
                )
                result.append(prediction_result)

            self.logger.info("Todos os passageiros foram salvos com sucesso.")

            return result

        except ValueError as ve:
            self.logger.error(f"Erro de validação: {str(ve)}")
            raise ValueError(f"Erro de validação: {str(ve)}")
        except Exception as e:
            self.logger.error(f"Erro inesperado: {str(e)}")
            raise Exception(f"Erro inesperado: {str(e)}")

    def get_all_passengers(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Recupera todos os passageiros do repositório com paginação estruturada."""
        try:
            result = self.passenger_repository.get_all(page=page, limit=limit)

            # Compatibilidade com repositórios que retornam apenas lista
            if isinstance(result, list):
                items = result
                total_items = len(items)
            elif not result or not result.get("items"):
                return {
                    "items": [],
                    "pagination": PaginationInfo(
                        page=page,
                        limit=limit,
                        total_items=0,
                        total_pages=0,
                        has_next=False,
                        has_previous=False,
                    ).model_dump(),
                }
            else:
                items = result["items"]
                total_items = result.get("total_count", len(items))

            # Converter itens para PassengerDetail
            passenger_details = []
            for item in items:
                detail = PassengerDetail(
                    passenger_id=item.get("passenger_id", ""),
                    survival_probability=float(item.get("survival_probability", 0)),
                    prediction=(
                        "survived"
                        if float(item.get("survival_probability", 0)) >= 0.5
                        else "not_survived"
                    ),
                    confidence_level=self._get_confidence_level(
                        float(item.get("survival_probability", 0))
                    ),
                    passenger_class=int(item.get("pclass", 0)),
                    sex=item.get("sex", ""),
                    age=float(item["age"]) if item.get("age") is not None else None,
                    siblings_spouses=int(item.get("sibsp", 0)),
                    parents_children=int(item.get("parch", 0)),
                    fare=float(item["fare"]) if item.get("fare") is not None else None,
                    embarked=item.get("embarked"),
                    created_at=item.get("created_at"),
                )
                passenger_details.append(detail.model_dump())

            total_pages = math.ceil(total_items / limit) if total_items > 0 else 0

            pagination = PaginationInfo(
                page=page,
                limit=limit,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
            )

            return {"items": passenger_details, "pagination": pagination.model_dump()}

        except Exception as e:
            self.logger.error(f"Erro ao recuperar passageiros: {str(e)}")
            raise Exception(f"Erro ao recuperar passageiros: {str(e)}")

    def get_passenger_by_id(self, passenger_id: str) -> Dict[str, Any]:
        """Recupera um passageiro pelo ID com formato estruturado."""
        try:
            item = self.passenger_repository.get_by_id(passenger_id)

            if not item:
                return None

            detail = PassengerDetail(
                passenger_id=item.get("passenger_id", ""),
                survival_probability=float(item.get("survival_probability", 0)),
                prediction=(
                    "survived"
                    if float(item.get("survival_probability", 0)) >= 0.5
                    else "not_survived"
                ),
                confidence_level=self._get_confidence_level(
                    float(item.get("survival_probability", 0))
                ),
                passenger_class=int(item.get("pclass", 0)),
                sex=item.get("sex", ""),
                age=float(item["age"]) if item.get("age") is not None else None,
                siblings_spouses=int(item.get("sibsp", 0)),
                parents_children=int(item.get("parch", 0)),
                fare=float(item["fare"]) if item.get("fare") is not None else None,
                embarked=item.get("embarked"),
                created_at=item.get("created_at"),
            )

            return detail.model_dump()

        except Exception as e:
            self.logger.error(
                f"Erro ao recuperar passageiro com ID {passenger_id}: {str(e)}"
            )
            raise Exception(
                f"Erro ao recuperar passageiro com ID {passenger_id}: {str(e)}"
            )

    def delete_passenger(self, passenger_id: str) -> DeleteResponse:
        """Exclui um passageiro pelo ID com resposta estruturada."""
        try:
            result = self.passenger_repository.delete(passenger_id)

            if result:
                return DeleteResponse(
                    deleted=True,
                    passenger_id=passenger_id,
                    message=f"Passageiro com ID {passenger_id} excluído com sucesso.",
                )
            else:
                return DeleteResponse(
                    deleted=False,
                    passenger_id=passenger_id,
                    message=f"Passageiro com ID {passenger_id} não encontrado.",
                )

        except Exception as e:
            self.logger.error(
                f"Erro ao excluir passageiro com ID {passenger_id}: {str(e)}"
            )
            raise Exception(
                f"Erro ao excluir passageiro com ID {passenger_id}: {str(e)}"
            )

    def _get_confidence_level(self, probability: float) -> str:
        """Determina o nível de confiança baseado na probabilidade."""
        if probability >= 0.8 or probability <= 0.2:
            return "high"
        elif probability >= 0.65 or probability <= 0.35:
            return "medium"
        else:
            return "low"
