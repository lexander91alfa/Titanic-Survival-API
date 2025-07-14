import pytest
from unittest.mock import patch, MagicMock
from src.config.app_config import AppConfig


class TestAppConfig:
    """Testes para a classe AppConfig."""

    @patch.dict('os.environ', {
        'DYNAMODB_TABLE_NAME': 'test-table',
        'AWS_REGION': 'us-west-2',
        'ENVIRONMENT': 'production',
        'LOG_LEVEL': 'DEBUG',
        'LOG_TYPE': 'file',
        'MODEL_PATH': 'models/test-model',
        'MODEL_METHOD': 'pickle'
    })
    def test_config_with_environment_variables(self):
        """Testa se a configuração carrega corretamente as variáveis de ambiente."""
        assert AppConfig.get_dynamodb_table_name() == 'test-table'
        assert AppConfig.get_aws_region() == 'us-west-2'
        assert AppConfig.get_environment() == 'production'
        assert AppConfig.get_log_level() == 'DEBUG'
        assert AppConfig.get_log_type() == 'file'
        assert AppConfig.get_model_path() == 'models/test-model'
        assert AppConfig.get_model_method() == 'pickle'

    @patch.dict('os.environ', {}, clear=True)
    def test_config_with_default_values(self):
        """Testa se a configuração usa valores padrão quando variáveis não estão definidas."""
        assert AppConfig.get_dynamodb_table_name() == 'titanic-passengers'
        assert AppConfig.get_aws_region() == 'us-east-1'
        assert AppConfig.get_environment() == 'development'
        assert AppConfig.get_log_level() == 'INFO'
        assert AppConfig.get_log_type() == 'console'
        assert AppConfig.get_model_path() == 'models/model'
        assert AppConfig.get_model_method() == 'joblib'

    @patch.dict('os.environ', {'ENVIRONMENT': 'production'})
    def test_is_production_true(self):
        """Testa se is_production retorna True para ambiente de produção."""
        assert AppConfig.is_production() is True
        assert AppConfig.is_development() is False

    @patch.dict('os.environ', {'ENVIRONMENT': 'development'})
    def test_is_development_true(self):
        """Testa se is_development retorna True para ambiente de desenvolvimento."""
        assert AppConfig.is_development() is True
        assert AppConfig.is_production() is False

    @patch.dict('os.environ', {'ENVIRONMENT': 'staging'})
    def test_environment_not_production_or_development(self):
        """Testa comportamento com ambiente que não é production nem development."""
        assert AppConfig.is_production() is False
        assert AppConfig.is_development() is False
