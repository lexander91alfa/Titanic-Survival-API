import pytest
from src.models.error_response import StandardErrorResponse, ErrorDetail


class TestErrorDetail:
    """Testes para o modelo ErrorDetail."""

    def test_error_detail_creation(self):
        """Testa criação de um ErrorDetail."""
        error_detail = ErrorDetail(
            field="age", message="Idade deve ser positiva", type="value_error"
        )

        assert error_detail.field == "age"
        assert error_detail.message == "Idade deve ser positiva"
        assert error_detail.type == "value_error"


class TestStandardErrorResponse:
    """Testes para o modelo StandardErrorResponse."""

    def test_standard_error_response_creation(self):
        """Testa criação de uma resposta de erro padrão."""
        error_response = StandardErrorResponse(message="Erro de teste", status_code=400)

        assert error_response.error is True
        assert error_response.message == "Erro de teste"
        assert error_response.details is None
        assert error_response.status_code == 400

    def test_validation_error_factory(self):
        """Testa criação de erro de validação via factory method."""
        validation_errors = [
            {
                "loc": ["age"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
            },
            {"loc": ["name"], "msg": "field required", "type": "value_error.missing"},
        ]

        error_response = StandardErrorResponse.validation_error(validation_errors)

        assert error_response.error is True
        assert error_response.message == "Erro de validação nos dados fornecidos"
        assert error_response.status_code == 422
        assert len(error_response.details) == 2

        # Verificar primeiro erro
        first_error = error_response.details[0]
        assert first_error.field == "age"
        assert first_error.message == "ensure this value is greater than 0"
        assert first_error.type == "value_error.number.not_gt"

        # Verificar segundo erro
        second_error = error_response.details[1]
        assert second_error.field == "name"
        assert second_error.message == "field required"
        assert second_error.type == "value_error.missing"

    def test_validation_error_with_empty_loc(self):
        """Testa criação de erro de validação com loc vazio."""
        validation_errors = [{"loc": [], "msg": "Invalid input", "type": "value_error"}]

        error_response = StandardErrorResponse.validation_error(validation_errors)

        assert len(error_response.details) == 1
        assert error_response.details[0].field == "unknown"

    def test_validation_error_with_missing_fields(self):
        """Testa criação de erro de validação com campos faltando."""
        validation_errors = [
            {
                # loc ausente
                "msg": "Some error",
                # type ausente
            }
        ]

        error_response = StandardErrorResponse.validation_error(validation_errors)

        assert len(error_response.details) == 1
        error_detail = error_response.details[0]
        assert error_detail.field == "unknown"
        assert error_detail.message == "Some error"
        assert error_detail.type == "unknown"

    def test_business_error_factory(self):
        """Testa criação de erro de negócio via factory method."""
        error_response = StandardErrorResponse.business_error(
            "Passageiro não encontrado", 404
        )

        assert error_response.error is True
        assert error_response.message == "Passageiro não encontrado"
        assert error_response.details is None
        assert error_response.status_code == 404

    def test_business_error_default_status_code(self):
        """Testa criação de erro de negócio com status code padrão."""
        error_response = StandardErrorResponse.business_error("Dados inválidos")

        assert error_response.status_code == 400

    def test_internal_error_factory(self):
        """Testa criação de erro interno via factory method."""
        error_response = StandardErrorResponse.internal_error(
            "Falha na conexão com o banco de dados"
        )

        assert error_response.error is True
        assert error_response.message == "Falha na conexão com o banco de dados"
        assert error_response.details is None
        assert error_response.status_code == 500

    def test_internal_error_default_message(self):
        """Testa criação de erro interno com mensagem padrão."""
        error_response = StandardErrorResponse.internal_error()

        assert error_response.message == "Erro interno do servidor"
        assert error_response.status_code == 500

    def test_error_response_serialization(self):
        """Testa serialização da resposta de erro."""
        error_detail = ErrorDetail(
            field="email", message="Invalid email format", type="value_error.email"
        )

        error_response = StandardErrorResponse(
            message="Validation failed", details=[error_detail], status_code=422
        )

        serialized = error_response.model_dump()

        expected = {
            "error": True,
            "message": "Validation failed",
            "details": [
                {
                    "field": "email",
                    "message": "Invalid email format",
                    "type": "value_error.email",
                }
            ],
            "status_code": 422,
        }

        assert serialized == expected
