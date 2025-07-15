from typing import Dict, Any
from src.services.predict_service import PredictionService
from src.repository.passenger_repository import PassengerRepository
from src.logging.custom_logging import get_logger
from src.config.app_config import AppConfig
from datetime import datetime
from time import time


class HealthCheck:
    """Classe para verificar a saúde dos componentes do sistema."""

    def __init__(self):
        self.logger = get_logger()

    def check_model_health(self) -> Dict[str, Any]:
        """Verifica se o modelo está carregado e funcionando."""
        try:
            start_time = time()
            self.logger.info("Iniciando verificação de saúde do modelo...")

            prediction_service = PredictionService(
                model_name="model.joblib", method=AppConfig.get_model_method()
            )

            test_data = {
                "Pclass": 3,
                "Sex": "male",
                "Age": 30.0,
                "SibSp": 0,
                "Parch": 0,
                "Fare": 10.0,
                "Embarked": "S",
            }

            probability = prediction_service.predict(test_data)

            elapsed_time = time() - start_time
            self.logger.info(
                f"Verificação de saúde do modelo concluída em {elapsed_time:.2f} segundos."
            )

            return {
                "status": "healthy",
                "message": "Modelo funcionando corretamente",
                "elapsed_time": elapsed_time,
                "test_data": test_data,
                "probability": probability,
            }

        except Exception as e:
            return {"status": "unhealthy", "message": f"Erro no modelo: {str(e)}"}

    def check_database_health(self) -> Dict[str, Any]:
        """Verifica se a conexão com o DynamoDB está funcionando."""
        try:
            repository = PassengerRepository()

            repository.get_all()

            return {"status": "healthy", "message": "Conexão com DynamoDB funcionando"}
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Erro na conexão com DynamoDB: {str(e)}",
            }

    def get_overall_health(self) -> Dict[str, Any]:
        """Retorna o status geral de saúde do sistema."""
        model_health = self.check_model_health()
        db_health = self.check_database_health()

        all_healthy = model_health["status"] == "healthy" and db_health["status"] in [
            "healthy",
            "skipped",
        ]

        return {
            "overall_status": "healthy" if all_healthy else "unhealthy",
            "components": {"model": model_health, "database": db_health},
            "environment": AppConfig.get_environment(),
            "uptime": datetime.now().isoformat(),
        }
