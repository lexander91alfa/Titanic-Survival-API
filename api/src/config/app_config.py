import os
from typing import Optional


class AppConfig:
    """Configurações da aplicação."""
    
    @classmethod
    def get_dynamodb_table_name(cls) -> str:
        """Retorna o nome da tabela DynamoDB."""
        return os.getenv("DYNAMODB_TABLE_NAME", "titanic-passengers")
    
    @classmethod 
    def get_aws_region(cls) -> str:
        """Retorna a região AWS."""
        return os.getenv("AWS_REGION", "us-east-1")
    
    @classmethod
    def get_environment(cls) -> str:
        """Retorna o ambiente atual."""
        return os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def get_log_level(cls) -> str:
        """Retorna o nível de log."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_log_type(cls) -> str:
        """Retorna o tipo de log."""
        return os.getenv("LOG_TYPE", "console")
    
    @classmethod
    def get_model_path(cls) -> str:
        """Retorna o caminho do modelo."""
        return os.getenv("MODEL_PATH", "models/model")
    
    @classmethod
    def get_model_method(cls) -> str:
        """Retorna o método de carregamento do modelo."""
        return os.getenv("MODEL_METHOD", "joblib")
    
    @classmethod
    def is_production(cls) -> bool:
        """Verifica se está em ambiente de produção."""
        return cls.get_environment().lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return cls.get_environment().lower() == "development"
