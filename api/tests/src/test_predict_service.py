import pytest
from unittest.mock import patch, MagicMock, mock_open
import numpy as np
import os
from src.services.predict_service import PredictionService, ModelConfig


class TestModelConfig:
    """Testes para a classe ModelConfig."""

    def test_model_config_constants(self):
        """Testa se as constantes estão definidas corretamente."""
        assert ModelConfig.DEFAULT_AGE == 29.7
        assert ModelConfig.DEFAULT_FARE == 32.2
        assert ModelConfig.DEFAULT_EMBARKED == "S"


class TestPredictionService:
    """Testes para a classe PredictionService."""

    @patch("src.services.predict_service.joblib.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_load_model_with_joblib_success(
        self, mock_join, mock_exists, mock_file, mock_joblib_load
    ):
        """Testa carregamento do modelo com joblib com sucesso."""
        # Arrange
        mock_join.return_value = "models/model"

        # Configure os.path.exists to return False for optimized file and True for regular file
        def mock_exists_side_effect(path):
            if path.endswith("_optimized.joblib"):
                return False
            elif path.endswith(".joblib"):
                return True
            return False

        mock_exists.side_effect = mock_exists_side_effect
        mock_model = MagicMock()
        mock_joblib_load.return_value = mock_model

        # Act
        service = PredictionService(
            model_name="model", method="joblib", lazy_loading=False
        )

        # Assert
        assert service.model == mock_model
        mock_file.assert_called_with("models/model.joblib", "rb")
        mock_joblib_load.assert_called_once()

    @patch("src.services.predict_service.pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_load_model_with_pickle_success(
        self, mock_join, mock_exists, mock_file, mock_pickle_load
    ):
        """Testa carregamento do modelo com pickle com sucesso."""
        # Arrange
        mock_join.return_value = "models/model"

        # Configure os.path.exists to return True for .pkl file
        def mock_exists_side_effect(path):
            if path.endswith(".pkl"):
                return True
            return False

        mock_exists.side_effect = mock_exists_side_effect
        mock_model = MagicMock()
        mock_pickle_load.return_value = mock_model

        # Act
        service = PredictionService(
            model_name="model", method="pickle", lazy_loading=False
        )

        # Assert
        assert service.model == mock_model
        mock_file.assert_called_with("models/model.pkl", "rb")
        mock_pickle_load.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.join")
    def test_load_model_invalid_method(self, mock_join, mock_exists):
        """Testa carregamento do modelo com método inválido."""
        # Arrange
        mock_join.return_value = "models/model"
        mock_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            PredictionService(
                model_name="model", method="invalid_method", lazy_loading=False
            )

        assert "Método de carregamento inválido" in str(exc_info.value)

    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_load_model_file_not_found(self, mock_join, mock_exists, mock_file):
        """Testa carregamento do modelo quando arquivo não existe."""
        # Arrange
        mock_join.return_value = "models/model"
        mock_exists.return_value = False  # Simula arquivo não encontrado

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            PredictionService(model_name="model", method="joblib", lazy_loading=False)

        assert "Nenhum arquivo de modelo encontrado para 'models/model'" in str(
            exc_info.value
        )

    @patch(
        "src.services.predict_service.joblib.load", side_effect=Exception("Load error")
    )
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_load_model_general_exception(
        self, mock_join, mock_exists, mock_file, mock_joblib_load
    ):
        """Testa carregamento do modelo com exceção geral."""
        # Arrange
        mock_join.return_value = "models/model"

        # Configure os.path.exists to return False for optimized file and True for regular file
        def mock_exists_side_effect(path):
            if path.endswith("_optimized.joblib"):
                return False
            elif path.endswith(".joblib"):
                return True
            return False

        mock_exists.side_effect = mock_exists_side_effect

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            PredictionService(model_name="model", method="joblib", lazy_loading=False)

        assert "Nenhum arquivo de modelo encontrado para 'models/model'" in str(
            exc_info.value
        )

    def test_preprocess_complete_data(self):
        """Testa preprocessamento com dados completos."""
        # Arrange
        with patch("src.services.predict_service.joblib.load"), patch(
            "builtins.open", new_callable=mock_open
        ), patch("os.path.join"), patch("os.path.exists", return_value=True):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 3,
            "Sex": "male",
            "Age": 22.0,
            "SibSp": 1,
            "Parch": 0,
            "Fare": 7.25,
            "Embarked": "S",
        }

        # Act
        result = service._preprocess(data)

        # Assert
        expected = np.array([[3, 22.0, 1, 0, 7.25, 1, 0, 1]])
        np.testing.assert_array_equal(result, expected)

    def test_preprocess_missing_optional_fields(self):
        """Testa preprocessamento com campos opcionais ausentes."""
        # Arrange
        with patch("src.services.predict_service.joblib.load"), patch(
            "builtins.open", new_callable=mock_open
        ), patch("os.path.join"), patch("os.path.exists", return_value=True):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 1,
            "Sex": "female",
            "SibSp": 0,
            "Parch": 1,
            # Age, Fare, Embarked ausentes
        }

        # Act
        result = service._preprocess(data)

        # Assert
        expected = np.array([[1, 29.7, 0, 1, 32.2, 0, 0, 1]])  # Valores padrão
        np.testing.assert_array_equal(result, expected)

    def test_preprocess_female_embarked_q(self):
        """Testa preprocessamento para mulher embarcada em Queenstown."""
        # Arrange
        with patch("src.services.predict_service.joblib.load"), patch(
            "builtins.open", new_callable=mock_open
        ), patch("os.path.join"), patch("os.path.exists", return_value=True):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 100.0,
            "Embarked": "Q",
        }

        # Act
        result = service._preprocess(data)

        # Assert
        expected = np.array(
            [[1, 25.0, 0, 0, 100.0, 0, 1, 0]]
        )  # embarked_q=1, sex_male=0
        np.testing.assert_array_equal(result, expected)

    def test_preprocess_embarked_c(self):
        """Testa preprocessamento para embarque em Cherbourg."""
        # Arrange
        with patch("src.services.predict_service.joblib.load"), patch(
            "builtins.open", new_callable=mock_open
        ), patch("os.path.join"), patch("os.path.exists", return_value=True):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 2,
            "Sex": "male",
            "Age": 30.0,
            "SibSp": 1,
            "Parch": 2,
            "Fare": 50.0,
            "Embarked": "C",
        }

        # Act
        result = service._preprocess(data)

        # Assert
        expected = np.array(
            [[2, 30.0, 1, 2, 50.0, 1, 0, 0]]
        )  # embarked_q=0, embarked_s=0
        np.testing.assert_array_equal(result, expected)

    def test_predict_success(self):
        """Testa predição com sucesso."""
        # Arrange
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])

        with patch(
            "src.services.predict_service.joblib.load", return_value=mock_model
        ), patch("builtins.open", new_callable=mock_open), patch("os.path.join"), patch(
            "os.path.exists", return_value=True
        ):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 100.0,
            "Embarked": "S",
        }

        # Act
        result = service.predict(data)

        # Assert
        assert result == 0.7
        mock_model.predict_proba.assert_called_once()

    def test_predict_model_not_loaded(self):
        """Testa predição quando modelo não foi carregado."""
        # Arrange
        with patch("src.services.predict_service.joblib.load"), patch(
            "builtins.open", new_callable=mock_open
        ), patch("os.path.join"), patch("os.path.exists", return_value=True):
            service = PredictionService(model_name="model", lazy_loading=False)

        service.model = None  # Simular modelo não carregado

        data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 100.0,
        }

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.predict(data)

        assert "Modelo não foi carregado" in str(exc_info.value)

    def test_predict_model_without_predict_proba(self):
        """Testa predição com modelo que não tem predict_proba."""
        # Arrange
        mock_model = MagicMock()
        del mock_model.predict_proba  # Remover o método

        with patch(
            "src.services.predict_service.joblib.load", return_value=mock_model
        ), patch("builtins.open", new_callable=mock_open), patch("os.path.join"), patch(
            "os.path.exists", return_value=True
        ):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 100.0,
        }

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.predict(data)

        assert "não possui o método predict_proba" in str(exc_info.value)

    def test_predict_probability_out_of_range_warning(self):
        """Testa predição que gera warning para probabilidade fora do range."""
        # Arrange
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array(
            [[0.0, 1.5]]
        )  # Probabilidade > 1

        with patch(
            "src.services.predict_service.joblib.load", return_value=mock_model
        ), patch("builtins.open", new_callable=mock_open), patch("os.path.join"), patch(
            "os.path.exists", return_value=True
        ):
            service = PredictionService(model_name="model", lazy_loading=False)

        data = {
            "Pclass": 1,
            "Sex": "female",
            "Age": 25.0,
            "SibSp": 0,
            "Parch": 0,
            "Fare": 100.0,
        }

        # Act
        with patch.object(service.logger, "warning") as mock_warning:
            result = service.predict(data)

        # Assert
        assert result == 1.5  # Retorna mesmo estando fora do range
        mock_warning.assert_called_once()

    def test_predict_preprocessing_exception(self):
        """Testa predição quando preprocessamento falha."""
        # Arrange
        mock_model = MagicMock()

        with patch(
            "src.services.predict_service.joblib.load", return_value=mock_model
        ), patch("builtins.open", new_callable=mock_open), patch("os.path.join"), patch(
            "os.path.exists", return_value=True
        ):
            service = PredictionService(model_name="model", lazy_loading=False)

        # Simular erro no preprocessamento
        with patch.object(
            service, "_preprocess", side_effect=Exception("Preprocessing error")
        ):
            data = {"Pclass": 1}

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                service.predict(data)

            assert "Preprocessing error" in str(exc_info.value)
