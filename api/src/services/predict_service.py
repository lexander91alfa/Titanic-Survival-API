import pickle
from typing import Any, Dict
import joblib
import numpy as np
from src.models.passenger_request import PassengerRequest
from src.logging.custom_logging import get_logger
from sys import path
import os


class ModelConfig:
    """Configurações padrão para preprocessing do modelo."""

    DEFAULT_AGE = 29.7  # Média da idade no dataset Titanic
    DEFAULT_FARE = 32.2  # Média da tarifa no dataset Titanic
    DEFAULT_EMBARKED = "S"  # Mais comum no dataset
    
    # Configurações de otimização
    USE_COMPRESSION = True  # Usar compressão para economia de espaço
    PREFERRED_METHOD = "pickle"  # pickle pode ser mais rápido que joblib para alguns modelos
    MODEL_CACHE_ENABLED = True  # Habilitar cache de modelo


class PredictionService:
    """
    Serviço encapsulado para carregar o modelo e realizar predições.
    Implementa lazy loading para otimizar o carregamento do modelo.
    """
    
    # Variável de classe para cache do modelo (singleton pattern)
    _model_cache = {}

    def __init__(self, model_name: str, method: str = "joblib", lazy_loading: bool = True):
        """
        Inicializa o serviço. O modelo será carregado apenas quando necessário (lazy loading).

        Args:
            model_name (str): O nome do modelo (usado para formar o caminho do arquivo).
            method (str): Método de carregamento ('joblib' ou 'pickle').
            lazy_loading (bool): Se True, usa lazy loading; se False, carrega imediatamente.
        """
        self.model_path = os.path.join("models", model_name)
        self.method = method
        self.logger = get_logger()
        self._model = None
        self.lazy_loading = lazy_loading
        
        # Chave única para cache baseada no caminho e método
        self._cache_key = f"{self.model_path}_{method}"
        
        # Se lazy loading está desabilitado, carrega o modelo imediatamente
        if not lazy_loading:
            self._model = self._load_model(method)

    @property
    def model(self):
        """
        Propriedade que implementa lazy loading do modelo.
        O modelo é carregado apenas quando acessado pela primeira vez.
        """
        if self._model is None and self.lazy_loading:
            # Verificar se o modelo já está no cache da classe
            if self._cache_key in self._model_cache:
                self.logger.info(f"Modelo '{self.model_path}' encontrado no cache.")
                self._model = self._model_cache[self._cache_key]
            else:
                self.logger.info(f"Carregando modelo '{self.model_path}' pela primeira vez.")
                self._model = self._load_model(self.method)
                # Armazenar no cache da classe para reutilização
                self._model_cache[self._cache_key] = self._model
        return self._model
    
    @model.setter
    def model(self, value):
        """
        Setter para a propriedade model (necessário para os testes).
        """
        self._model = value

    def _load_model(self, method: str = "joblib") -> Any:
        """
        Método privado para carregar o modelo a partir do arquivo.
        Levanta um erro se o modelo não puder ser encontrado ou carregado.
        Implementa otimizações para carregamento mais rápido.
        """
        try:
            # Tentar métodos em ordem de preferência para performance
            load_methods = []
            
            if method == "joblib":
                load_methods = [
                    ("joblib_compressed", f"{self.model_path}_optimized.joblib"),
                    ("joblib", f"{self.model_path}.joblib")
                ]
            elif method == "pickle":
                load_methods = [
                    ("pickle", f"{self.model_path}.pkl"),
                    ("joblib", f"{self.model_path}.joblib")  # Fallback
                ]
            else:
                raise ValueError(
                    "Método de carregamento inválido. Use 'joblib' ou 'pickle'."
                )
            
            model = None
            actual_method = None
            
            for load_method, file_path in load_methods:
                if os.path.exists(file_path):
                    self.logger.info(f"Tentando carregar modelo com {load_method} de '{file_path}'")
                    
                    try:
                        if load_method == "joblib" or load_method == "joblib_compressed":
                            with open(file_path, "rb") as f:
                                model = joblib.load(f)
                        elif load_method == "pickle":
                            with open(file_path, "rb") as f:
                                model = pickle.load(f)
                        
                        actual_method = load_method
                        self.logger.info(f"Modelo carregado com sucesso usando {load_method}")
                        break
                        
                    except Exception as e:
                        self.logger.warning(f"Falha ao carregar com {load_method}: {e}")
                        continue
                else:
                    self.logger.debug(f"Arquivo não encontrado: {file_path}")
            
            if model is None:
                raise FileNotFoundError(
                    f"Nenhum arquivo de modelo encontrado para '{self.model_path}'"
                )
            
            return model
            
        except FileNotFoundError:
            self.logger.error(
                f"ERRO: Arquivo do modelo não encontrado em '{self.model_path}'"
            )
            raise
        except Exception as e:
            self.logger.error(f"ERRO: Não foi possível carregar o modelo. Causa: {e}")
            raise

    def _preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Método privado para pré-processar os dados da requisição.
        Converte os dados em um array NumPy na ordem correta, com encoding.

        Args:
            data (Dict[str, Any]): Dicionário com os dados do passageiro.

        Returns:
            np.ndarray: Um array 2D NumPy pronto para o modelo.
        """

        try:
            # Usar valores padrão baseados em estatísticas do dataset
            age = (
                data.get("Age")
                if data.get("Age") is not None
                else ModelConfig.DEFAULT_AGE
            )
            fare = (
                data.get("Fare")
                if data.get("Fare") is not None
                else ModelConfig.DEFAULT_FARE
            )
            embarked = (
                data.get("Embarked")
                if data.get("Embarked") is not None
                else ModelConfig.DEFAULT_EMBARKED
            )

            sex_male = 1 if data.get("Sex") == "male" else 0

            embarked_q = 1 if embarked == "Q" else 0
            embarked_s = 1 if embarked == "S" else 0

            feature_vector = [
                data.get("Pclass"),
                age,
                data.get("SibSp"),
                data.get("Parch"),
                fare,
                sex_male,
                embarked_q,
                embarked_s,
            ]

            self.logger.debug(f"Feature vector criado: {feature_vector}")
            return np.array([feature_vector])
        except Exception as e:
            self.logger.error(f"ERRO: Falha no pré-processamento dos dados. Causa: {e}")
            raise

    def predict(self, request_data: Dict[str, Any]) -> float:
        """
        Realiza a predição de sobrevivência com base nos dados da requisição.

        Args:
            request_data (Dict[str, Any]): Os dados do passageiro validados.

        Returns:
            float: A probabilidade de sobrevivência (um valor entre 0.0 e 1.0).
        """
        try:
            processed_features = self._preprocess(request_data)

            probability_prediction = self.model.predict_proba(processed_features)

            survival_probability = probability_prediction[0][1]

            # Validar se a probabilidade está no range esperado
            if not 0.0 <= survival_probability <= 1.0:
                self.logger.warning(
                    f"Probabilidade fora do range esperado: {survival_probability}"
                )

            self.logger.info(
                f"Predição realizada com sucesso: {survival_probability:.4f}"
            )
            
            return survival_probability
        except Exception as e:
            self.logger.error(f"ERRO: Falha na predição. Causa: {e}")
            raise

    @classmethod
    def clear_model_cache(cls):
        """
        Limpa o cache de modelos da classe.
        Útil para testes ou quando se quer forçar o recarregamento.
        """
        cls._model_cache.clear()
    
    @classmethod
    def get_cache_info(cls):
        """
        Retorna informações sobre o cache atual.
        """
        return {
            "cached_models": list(cls._model_cache.keys()),
            "cache_size": len(cls._model_cache)
        }
