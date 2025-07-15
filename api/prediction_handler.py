from src.models.passenger_request import PassengerRequest
from src.models.error_response import StandardErrorResponse
from src.models.api_response import HealthResponse, HealthStatus
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
    logger = get_logger()
    
    
    try:
        http_adapter = HTTPAdapter(event)
        http_method = http_adapter.method

        event.pop("x-api-key")

        logger.info(event)

        logger.info(f"Requisição recebida: {http_method} {http_adapter.path}")

        match http_method:
            case "POST":
                request_data = http_adapter.body

                if isinstance(request_data, list):
                    passengers = [PassengerRequest(**data) for data in request_data]
                else:
                    passengers = [PassengerRequest(**request_data)]

                predictions = passenger_controller.save_passenger(passengers)

                if len(predictions) == 1:
                    result = predictions[0].model_dump()
                    return http_adapter.build_standard_response(
                        201, 
                        result, 
                        request_id=http_adapter.request_id,
                        message="Predição de sobrevivência realizada com sucesso"
                    )
                else:
                    results = [p.model_dump() for p in predictions]
                    return http_adapter.build_standard_response(
                        201,
                        results,
                        request_id=http_adapter.request_id,
                        message="Predições de sobrevivência realizadas com sucesso"
                    )

            case "GET":
                if http_adapter.path == "/health":
                    health_check = HealthCheck()
                    health_status = health_check.get_overall_health()
                    
                    health_response = HealthResponse(
                        overall_status=health_status.get("overall_status", "unhealthy"),
                        components=health_status.get("components", {}),
                        uptime=health_status.get("uptime"),
                    )
                    
                    status_code = 200 if health_status["overall_status"] == "healthy" else 503

                    health_response.metadata.request_id = http_adapter.request_id

                    return http_adapter.build_standard_response(
                        status_code, 
                        health_response,
                        request_id=http_adapter.request_id,
                        message="Status de saúde do serviço"
                    )
                    
                elif http_adapter.path == "/sobreviventes":
                    if http_adapter.query_parameters:
                        query_params = http_adapter.query_parameters
                        page = int(query_params.get("page", 1))
                        limit = int(query_params.get("limit", 10))
                    else:
                        page, limit = 1, 10

                    result = passenger_controller.get_all_passengers(page=page, limit=limit)
                    
                    if result.get("items"):
                        # Retornar com informação de paginação
                        response_data = {
                            "passengers": result["items"],
                            "pagination": result["pagination"]
                        }
                        return http_adapter.build_standard_response(
                            200, 
                            response_data,
                            request_id=http_adapter.request_id,
                            message="Lista de passageiros recuperada com sucesso"
                        )
                    else:
                        return http_adapter.build_standard_response(
                            404, 
                            {"error": "Nenhum passageiro encontrado"},
                            request_id=http_adapter.request_id
                        )

                elif http_adapter.resource == "/sobreviventes/{id}":
                    passenger_id = http_adapter.path_parameters.get("id")
                    if not passenger_id:
                        error_response = StandardErrorResponse.business_error(
                            "ID do passageiro é obrigatório", 400
                        )
                        return http_adapter.build_standard_response(
                            400, error_response, request_id=http_adapter.request_id
                        )

                    passenger = passenger_controller.get_passenger_by_id(passenger_id)
                    if not passenger:
                        error_response = StandardErrorResponse.business_error(
                            "Passageiro não encontrado", 404
                        )
                        return http_adapter.build_standard_response(
                            404, error_response, request_id=http_adapter.request_id
                        )
                    
                    return http_adapter.build_standard_response(
                        200, 
                        passenger,
                        request_id=http_adapter.request_id,
                        message="Dados do passageiro recuperados com sucesso"
                    )

            case "DELETE":
                passenger_id = http_adapter.path_parameters.get("id")
                if not passenger_id:
                    error_response = StandardErrorResponse.business_error(
                        "ID do passageiro é obrigatório para exclusão", 400
                    )
                    return http_adapter.build_standard_response(
                        400, error_response, request_id=http_adapter.request_id
                    )

                delete_result = passenger_controller.delete_passenger(passenger_id)
                status_code = 200 if delete_result.deleted else 404
                message = "Passageiro excluído com sucesso" if delete_result.deleted else "Passageiro não encontrado"
                
                return http_adapter.build_standard_response(
                    status_code, 
                    delete_result,
                    request_id=http_adapter.request_id,
                    message=message
                )
            case _:
                error_response = StandardErrorResponse.business_error(
                    "Método HTTP não permitido", 405
                )
                return http_adapter.build_standard_response(
                    405, error_response, request_id=http_adapter.request_id
                )

    except ValidationError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        error_response = StandardErrorResponse.validation_error(ve.errors())
        return http_adapter.build_standard_response(
            error_response.status_code, error_response, request_id=http_adapter.request_id
        )
    except ValueError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        error_response = StandardErrorResponse.business_error(str(ve))
        return http_adapter.build_standard_response(
            error_response.status_code, error_response, request_id=http_adapter.request_id
        )
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        error_response = StandardErrorResponse.internal_error()
        return http_adapter.build_standard_response(
            error_response.status_code, error_response, request_id=http_adapter.request_id
        )


