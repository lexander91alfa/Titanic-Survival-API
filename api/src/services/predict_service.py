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


class PredictionService:
    """
    Serviço encapsulado para carregar o modelo e realizar predições.
    """

    def __init__(self, model_name: str, method: str = "joblib"):
        """
        Inicializa o serviço carregando o modelo a partir do caminho especificado.

        Args:
            model (str): O caminho para o arquivo .pkl do modelo.
                              O caminho é relativo à raiz da função Lambda.
        """
        self.model_path = os.path.join("models", model_name)
        self.logger = get_logger()
        self.model = self._load_model(method)

    def _load_model(self, method: str = "joblib") -> Any:
        """
        Método privado para carregar o modelo a partir do arquivo .pkl.
        Levanta um erro se o modelo não puder ser encontrado ou carregado.
        """
        try:
            if method == "joblib":
                self.logger.info(f"Carregando modelo com joblib de '{self.model_path}'")
                with open(f"{self.model_path}.joblib", "rb") as f:
                    model = joblib.load(f)
            elif method == "pickle":
                self.logger.info(f"Carregando modelo com pickle de '{self.model_path}'")
                with open(f"{self.model_path}.pkl", "rb") as f:
                    model = pickle.load(f)
            else:
                raise ValueError(
                    "Método de carregamento inválido. Use 'joblib' ou 'pickle'."
                )
            self.logger.info(f"Modelo '{self.model_path}' carregado com sucesso.")
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
            age = data.get("Age") if data.get("Age") is not None else ModelConfig.DEFAULT_AGE
            fare = data.get("Fare") if data.get("Fare") is not None else ModelConfig.DEFAULT_FARE
            embarked = data.get("Embarked") if data.get("Embarked") is not None else ModelConfig.DEFAULT_EMBARKED

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
            if not self.model:
                raise RuntimeError(
                    "Modelo não foi carregado. Não é possível fazer a predição."
                )

            # Validar se o modelo tem o método predict_proba
            if not hasattr(self.model, 'predict_proba'):
                raise RuntimeError(
                    "Modelo carregado não possui o método predict_proba necessário."
                )

            processed_features = self._preprocess(request_data)

            probability_prediction = self.model.predict_proba(processed_features)

            survival_probability = probability_prediction[0][1]

            # Validar se a probabilidade está no range esperado
            if not 0.0 <= survival_probability <= 1.0:
                self.logger.warning(f"Probabilidade fora do range esperado: {survival_probability}")

            self.logger.info(f"Predição realizada com sucesso: {survival_probability:.4f}")
            return survival_probability
        except Exception as e:
            self.logger.error(f"ERRO: Falha na predição. Causa: {e}")
            raise
