from src.models.passeger_request import PassengerRequest
from src.controllers.passenger_controller import PassengerController
from src.logging.custom_logging import get_logger
from src.adapter.http_adapter import HTTPAdapter
from pydantic import ValidationError


def lambda_handler(event, _):
    """Função Lambda para lidar com requisições HTTP."""
    try:
        passenger_controller = PassengerController()
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
                        "probability": result.probability
                    }
                    return http_adapter.build_response(201, formatted_result)
                else:
                    return http_adapter.build_response(201, passengers_with_survival_probability)

            case "GET":
                if http_adapter.path == "/sobreviventes":
                    passengers = passenger_controller.get_all_passengers()
                    return http_adapter.build_response(200, passengers)
                elif http_adapter.resource == "/sobreviventes/{id}":
                    passenger_id = http_adapter.path_parameters.get("id")
                    if not passenger_id:
                        return http_adapter.build_response(
                            400, {"error": "ID do passageiro é obrigatório"}
                        )
                    passenger = passenger_controller.get_passenger_by_id(passenger_id)
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
                    return http_adapter.build_response(200, result)

            case _:
                return http_adapter.build_response(
                    405, {"error": "Método HTTP não permitido"}
                )

    except ValidationError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        errors = []
        for error in ve.errors():
            errors.append({
                "field": error.get("loc", ["unknown"])[0] if error.get("loc") else "unknown",
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "unknown")
            })
        return http_adapter.build_response(422, {
            "detail": "Validation Error",
            "errors": errors
        })

    except ValueError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        return http_adapter.build_response(400, {"error": str(ve)})

    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return http_adapter.build_response(500, {"error": str(e)})
