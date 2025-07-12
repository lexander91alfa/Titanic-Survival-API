import pickle
import joblib
import numpy as np
from src.models.passeger_request import PassengerRequest
from sys import path
import os


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
        self.model = self._load_model(method)
        self.feature_order = [
            "Pclass",
            "SibSp",
            "Age",
            "Parch",
            "Fare",
            "Sex_male",
            "Embarked_Q",
            "Embarked_S",
        ]

    def _load_model(self, method: str = "joblib"):
        """
        Método privado para carregar o modelo a partir do arquivo .pkl.
        Levanta um erro se o modelo não puder ser encontrado ou carregado.
        """
        try:
            if method == "joblib":
                print(f"Carregando modelo com joblib de '{self.model_path}'")
                with open(f"{self.model_path}.joblib", "rb") as f:
                    model = joblib.load(f)
            elif method == "pickle":
                print(f"Carregando modelo com pickle de '{self.model_path}'")
                with open(f"{self.model_path}.pkl", "rb") as f:
                    model = pickle.load(f)
            else:
                raise ValueError(
                    "Método de carregamento inválido. Use 'joblib' ou 'pickle'."
                )
            print(f"Modelo '{self.model_path}' carregado com sucesso.")
            return model
        except FileNotFoundError:
            print(f"ERRO: Arquivo do modelo não encontrado em '{self.model_path}'")
            raise
        except Exception as e:
            print(f"ERRO: Não foi possível carregar o modelo. Causa: {e}")
            raise

    def _preprocess(self, request_data: PassengerRequest) -> np.ndarray:
        """
        Método privado para pré-processar os dados da requisição.
        Converte os dados em um array NumPy na ordem correta, com encoding.

        Args:
            request_data (PassengerRequest): O objeto Pydantic com os dados de entrada.

        Returns:
            np.ndarray: Um array 2D NumPy pronto para o modelo.
        """
        data = request_data.model_dump()

        features_list = [
            data.get(feature) for feature in self.feature_order
        ]

        return np.array(features_list).reshape(1, -1)

    def predict(self, request_data: PassengerRequest) -> float:
        """
        Realiza a predição de sobrevivência com base nos dados da requisição.

        Args:
            request_data (PassengerRequest): Os dados do passageiro validados.

        Returns:
            float: A probabilidade de sobrevivência (um valor entre 0.0 e 1.0).
        """
        if not self.model:
            raise RuntimeError(
                "Modelo não foi carregado. Não é possível fazer a predição."
            )

        processed_features = self._preprocess(request_data)

        probability_prediction = self.model.predict_proba(processed_features)

        survival_probability = probability_prediction[0][1]

        return survival_probability
