import pytest
from unittest.mock import patch, MagicMock, mock_open
import numpy as np
import os
from src.services.predict_service import PredictionService


class TestPredictionService:
    """Testes para a classe PredictionService."""

    @patch("src.services.predict_service.joblib.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_load_model_with_joblib_success(
        self, mock_exists, mock_file, mock_joblib_load
    ):
        """Testa carregamento do modelo com joblib com sucesso em ambiente local."""
        # Arrange
        # 1. Chamada em __init__ para verificar /opt/python/modelos (False)
        # 2. Chamada em _load_model para verificar modelos/model.joblib (True)
        mock_exists.side_effect = [False, True]
        mock_model = MagicMock()
        mock_joblib_load.return_value = mock_model

        # Act
        service = PredictionService(model_name="model", method="joblib")

        # Assert
        assert service.model == mock_model
        mock_file.assert_called_with("modelos/model.joblib", "rb")
        mock_joblib_load.assert_called_once()

    @patch("src.services.predict_service.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_load_model_with_pickle_success(
        self, mock_exists, mock_file, mock_pickle_load
    ):
        """Testa carregamento do modelo com pickle com sucesso."""
        # Arrange
        mock_exists.side_effect = [False, True]  # local env, file exists
        mock_model = MagicMock()
        mock_pickle_load.return_value = mock_model

        # Act
        service = PredictionService(model_name="model", method="pickle")

        # Assert
        assert service.model == mock_model
        mock_file.assert_called_with("modelos/model.pkl", "rb")
        mock_pickle_load.assert_called_once()

    @patch("os.path.exists")
    def test_load_model_in_lambda_env(self, mock_exists):
        """Testa o carregamento do modelo no ambiente Lambda."""
        # Arrange
        # 1. Chamada em __init__ para verificar /opt/python/modelos (True)
        # 2. Chamada em _load_model para verificar /opt/python/modelos/model.joblib (True)
        mock_exists.side_effect = [True, True]

        # Mock open e joblib.load para evitar erro de arquivo real
        with patch("builtins.open", mock_open()) as mock_file, patch(
            "src.services.predict_service.joblib.load"
        ) as mock_joblib_load:
            mock_model = MagicMock()
            mock_joblib_load.return_value = mock_model

            # Act
            service = PredictionService(model_name="model", method="joblib")

            # Assert
            assert service.model_path == os.path.join("/opt/python/modelos", "model")
            mock_file.assert_called_with(
                os.path.join("/opt/python/modelos", "model.joblib"), "rb"
            )
            mock_joblib_load.assert_called_once()

    @patch("os.path.exists")
    def test_load_model_invalid_method(self, mock_exists):
        """Testa carregamento do modelo com método inválido."""
        # Arrange
        mock_exists.return_value = False

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            PredictionService(model_name="model", method="invalid_method")

        assert "Método de carregamento inválido" in str(exc_info.value)

    @patch("os.path.exists")
    def test_load_model_file_not_found(self, mock_exists):
        """Testa carregamento do modelo quando arquivo não existe."""
        # Arrange
        # 1. /opt/python/modelos não existe
        # 2. modelos/model.joblib não existe
        mock_exists.side_effect = [False, False]

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            PredictionService(model_name="model", method="joblib")

        assert "Arquivo não encontrado: modelos/model.joblib" in str(exc_info.value)

    @patch(
        "src.services.predict_service.joblib.load", side_effect=Exception("Load error")
    )
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_load_model_general_exception(
        self, mock_exists, mock_file, mock_joblib_load
    ):
        """Testa carregamento do modelo com exceção geral."""
        # Arrange
        mock_exists.side_effect = [False, True]  # local env, file exists

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            PredictionService(model_name="model", method="joblib")

        assert "Não foi possível carregar o modelo. Causa: Load error" in str(
            exc_info.value
        )

    def test_preprocess_complete_data(self):
        """Testa preprocessamento com dados completos."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        service.model = MagicMock()  # Evita o carregamento real do modelo

        request_data = {
            "Pclass": 3,
            "Sex": "male",
            "Age": 22.0,
            "SibSp": 1,
            "Parch": 0,
            "Fare": 7.25,
            "Embarked": "S",
        }

        # Act
        processed_data = service._preprocess(request_data)

        # Assert
        expected_array = np.array([[3, 22.0, 1, 0, 7.25, 1, 0, 1]])
        np.testing.assert_array_equal(processed_data, expected_array)

    def test_preprocess_missing_data(self):
        """Testa preprocessamento com dados faltantes (usando defaults)."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        service.model = MagicMock()

        request_data = {
            "Pclass": 1,
            "Sex": "female",
            "SibSp": 0,
            "Parch": 0,
        }

        # Act
        processed_data = service._preprocess(request_data)

        # Assert
        # Defaults: Age=29.7, Fare=32.2, Embarked='S'
        expected_array = np.array([[1, 29.7, 0, 0, 32.2, 0, 0, 1]])
        np.testing.assert_array_equal(processed_data, expected_array)

    def test_preprocess_different_sex_embarked(self):
        """Testa preprocessamento com 'female' e 'Embarked' diferente."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        service.model = MagicMock()

        request_data = {
            "Pclass": 2,
            "Sex": "female",
            "Age": 30.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 15.0,
            "Embarked": "Q",
        }

        # Act
        processed_data = service._preprocess(request_data)

        # Assert
        # sex_male=0, embarked_q=1, embarked_s=0
        expected_array = np.array([[2, 30.0, 0, 0, 15.0, 0, 1, 0]])
        np.testing.assert_array_equal(processed_data, expected_array)

    def test_predict_success(self):
        """Testa a predição com sucesso."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        mock_model = MagicMock()
        # Retorna a probabilidade de [classe_0, classe_1]
        mock_model.predict_proba.return_value = np.array([[0.2, 0.8]])
        service.model = mock_model

        request_data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 38.0,
            "SibSp": 1,
            "Parch": 0,
            "Fare": 71.2833,
            "Embarked": "C",
        }

        # Act
        probability = service.predict(request_data)

        # Assert
        assert probability == 0.8
        service.model.predict_proba.assert_called_once()

    def test_predict_model_not_loaded(self):
        """Testa a predição quando o modelo não está carregado."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        service.model = None  # Simula modelo não carregado

        request_data = {"Pclass": 1, "Sex": "female", "Age": 38.0}

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.predict(request_data)

        assert "Modelo não foi carregado" in str(exc_info.value)

    def test_predict_model_no_predict_proba(self):
        """Testa a predição quando o modelo não tem 'predict_proba'."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        service.model = object()  # Um objeto sem o método predict_proba

        request_data = {"Pclass": 1, "Sex": "female", "Age": 38.0}

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.predict(request_data)

        assert "não possui o método predict_proba" in str(exc_info.value)

    def test_predict_preprocessing_fails(self):
        """Testa a predição quando o pré-processamento falha."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        service.model = MagicMock()

        # Dados inválidos que causarão um erro no _preprocess
        request_data = {"Sex": "male"}  # Faltando Pclass

        # Act & Assert
        with pytest.raises(Exception):
            service.predict(request_data)

    def test_predict_prediction_fails(self):
        """Testa a predição quando a chamada a predict_proba falha."""
        # Arrange
        service = PredictionService(model_name="model", method="joblib")
        mock_model = MagicMock()
        mock_model.predict_proba.side_effect = Exception("Prediction error")
        service.model = mock_model

        request_data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 38.0,
            "SibSp": 1,
            "Parch": 0,
            "Fare": 71.2833,
            "Embarked": "C",
        }

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            service.predict(request_data)

        assert "Falha na predição. Causa: Prediction error" in str(exc_info.value)

    # Mock os.path.exists para todos os testes de predição e pré-processamento
    # para que o construtor não falhe ao tentar carregar o modelo.
    @pytest.fixture(autouse=True)
    def mock_os_path_exists_for_init(self):
        with patch("os.path.exists") as mock_exists:
            # Simula que o arquivo do modelo existe para que o construtor não falhe
            mock_exists.return_value = True
            with patch("builtins.open", mock_open()), patch(
                "src.services.predict_service.joblib.load"
            ), patch("src.services.predict_service.pickle.load"):
                yield
