from src.models.passenger_request import PassengerRequest
from src.models.error_response import StandardErrorResponse
from src.controllers.passenger_controller import PassengerController
from src.middleware.health_check import HealthCheck
from src.logging.custom_logging import get_logger
from src.adapter.http_adapter import HTTPAdapter
from pydantic import ValidationError

# Instanciar o controller fora da função para reutilizar entre chamadas
# Isso evita recarregar o modelo a cada requisição (cold start optimization)
passenger_controller = PassengerController()


def lambda_handler(event, _):
    """Função Lambda para lidar com requisições HTTP."""
    try:
        logger = get_logger()
        http_adapter = HTTPAdapter(event)
        http_method = http_adapter.method

        logger.info(f"Requisição recebida: {http_method} {http_adapter.path}")

        match http_method:
            case "POST":
                request_data = http_adapter.body

                if isinstance(request_data, list):
                    passengers = [PassengerRequest(**data) for data in request_data]
                else:
                    passengers = [PassengerRequest(**request_data)]

                passengers_with_survival_probability = (
                    passenger_controller.save_passenger(passengers)
                )

                if len(passengers_with_survival_probability) == 1:
                    result = passengers_with_survival_probability[0]
                    formatted_result = {
                        "PassengerId": result.id,
                        "probability": result.probability,
                    }
                    return http_adapter.build_response(201, formatted_result)
                else:
                    return http_adapter.build_response(
                        201,
                        [p.model_dump() for p in passengers_with_survival_probability],
                    )

            case "GET":
                if http_adapter.path == "/health":
                    health_check = HealthCheck()
                    health_status = health_check.get_overall_health()
                    status_code = (
                        200 if health_status["overall_status"] == "healthy" else 503
                    )
                    return http_adapter.build_response(status_code, health_status)
                elif http_adapter.path == "/sobreviventes":
                    if http_adapter.query_parameters:
                        query_params = http_adapter.query_parameters
                        page = query_params.get("page")
                        limit = query_params.get("limit")

                        if page is not None and limit is not None:
                            passengers = passenger_controller.get_all_passengers(
                                page=page, limit=limit
                            )
                        else:
                            passengers = passenger_controller.get_all_passengers()
                    else:
                        passengers = passenger_controller.get_all_passengers()

                    if passengers.get("items"):
                        return http_adapter.build_response(200, passengers["items"])
                    else:
                        return http_adapter.build_response(404, {"error": "Nenhum passageiro encontrado"})

                elif http_adapter.resource == "/sobreviventes/{id}":
                    passenger_id = http_adapter.path_parameters.get("id")
                    if not passenger_id:
                        return http_adapter.build_response(
                            400, {"error": "ID do passageiro é obrigatório"}
                        )

                    passenger = passenger_controller.get_passenger_by_id(passenger_id)
                    if not passenger:
                        return http_adapter.build_response(
                            404, {"error": "Passageiro não encontrado"}
                        )
                    
                    return http_adapter.build_response(200, passenger)

            case "DELETE":
                if http_adapter.path_parameters.get("id"):
                    passenger_id = http_adapter.path_parameters.get("id")
                    if not passenger_id:
                        return http_adapter.build_response(
                            400,
                            {"error": "ID do passageiro é obrigatório para exclusão"},
                        )

                    result = passenger_controller.delete_passenger(passenger_id)
                    return http_adapter.build_response(result.get("status_code", 500), {"message": result.get("message", "Erro ao deletar passageiro")})
                else:
                    return http_adapter.build_response(
                        400,
                        {"error": "ID do passageiro é obrigatório para exclusão"},
                    )
            case _:
                return http_adapter.build_response(
                    405, {"error": "Método HTTP não permitido"}
                )

    except ValidationError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        error_response = StandardErrorResponse.validation_error(ve.errors())
        return http_adapter.build_response(
            error_response.status_code, error_response.model_dump()
        )
    except ValueError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        error_response = StandardErrorResponse.business_error(str(ve))
        return http_adapter.build_response(
            error_response.status_code, error_response.model_dump()
        )
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        error_response = StandardErrorResponse.internal_error()
        return http_adapter.build_response(
            error_response.status_code, error_response.model_dump()
        )


