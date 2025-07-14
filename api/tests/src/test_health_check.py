import pytest
from unittest.mock import patch, MagicMock
from src.middleware.health_check import HealthCheck
from src.config.app_config import AppConfig


class TestHealthCheck:
    """Testes para a classe HealthCheck."""

    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.health_check = HealthCheck()

    @patch('src.middleware.health_check.PredictionService')
    def test_check_model_health_success(self, mock_prediction_service):
        """Testa verificação de saúde do modelo com sucesso."""
        # Arrange
        mock_service_instance = MagicMock()
        mock_service_instance.predict.return_value = 0.75
        mock_prediction_service.return_value = mock_service_instance

        # Act
        result = self.health_check.check_model_health()

        # Assert
        assert result["status"] == "healthy"
        assert result["message"] == "Modelo funcionando corretamente"
        assert result["test_probability"] == 0.75
        mock_prediction_service.assert_called_once_with(
            model_name="model", 
            method=AppConfig.MODEL_METHOD
        )

    @patch('src.middleware.health_check.PredictionService')
    def test_check_model_health_failure(self, mock_prediction_service):
        """Testa verificação de saúde do modelo com falha."""
        # Arrange
        mock_prediction_service.side_effect = Exception("Modelo não encontrado")

        # Act
        result = self.health_check.check_model_health()

        # Assert
        assert result["status"] == "unhealthy"
        assert "Modelo não encontrado" in result["message"]

    @patch.object(AppConfig, 'is_development', return_value=True)
    def test_check_database_health_development_skipped(self, mock_is_dev):
        """Testa que a verificação de DB é pulada em desenvolvimento."""
        # Act
        result = self.health_check.check_database_health()

        # Assert
        assert result["status"] == "skipped"
        assert "desenvolvimento" in result["message"]

    @patch.object(AppConfig, 'is_development', return_value=False)
    @patch('src.middleware.health_check.PassengerRepository')
    def test_check_database_health_success(self, mock_repository, mock_is_dev):
        """Testa verificação de saúde do banco com sucesso."""
        # Arrange
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_all.return_value = []
        mock_repository.return_value = mock_repo_instance

        # Act
        result = self.health_check.check_database_health()

        # Assert
        assert result["status"] == "healthy"
        assert "DynamoDB funcionando" in result["message"]

    @patch.object(AppConfig, 'is_development', return_value=False)
    @patch('src.middleware.health_check.PassengerRepository')
    def test_check_database_health_failure(self, mock_repository, mock_is_dev):
        """Testa verificação de saúde do banco com falha."""
        # Arrange
        mock_repository.side_effect = Exception("Conexão falhou")

        # Act
        result = self.health_check.check_database_health()

        # Assert
        assert result["status"] == "unhealthy"
        assert "Conexão falhou" in result["message"]

    @patch.object(HealthCheck, 'check_model_health')
    @patch.object(HealthCheck, 'check_database_health')
    def test_get_overall_health_all_healthy(self, mock_db_health, mock_model_health):
        """Testa status geral quando todos os componentes estão saudáveis."""
        # Arrange
        mock_model_health.return_value = {"status": "healthy"}
        mock_db_health.return_value = {"status": "healthy"}

        # Act
        result = self.health_check.get_overall_health()

        # Assert
        assert result["overall_status"] == "healthy"
        assert "model" in result["components"]
        assert "database" in result["components"]
        assert "environment" in result

    @patch.object(HealthCheck, 'check_model_health')
    @patch.object(HealthCheck, 'check_database_health')
    def test_get_overall_health_model_unhealthy(self, mock_db_health, mock_model_health):
        """Testa status geral quando o modelo não está saudável."""
        # Arrange
        mock_model_health.return_value = {"status": "unhealthy"}
        mock_db_health.return_value = {"status": "healthy"}

        # Act
        result = self.health_check.get_overall_health()

        # Assert
        assert result["overall_status"] == "unhealthy"

    @patch.object(HealthCheck, 'check_model_health')
    @patch.object(HealthCheck, 'check_database_health')
    def test_get_overall_health_db_skipped_still_healthy(self, mock_db_health, mock_model_health):
        """Testa que status geral é healthy mesmo quando DB é pulado."""
        # Arrange
        mock_model_health.return_value = {"status": "healthy"}
        mock_db_health.return_value = {"status": "skipped"}

        # Act
        result = self.health_check.get_overall_health()

        # Assert
        assert result["overall_status"] == "healthy"
