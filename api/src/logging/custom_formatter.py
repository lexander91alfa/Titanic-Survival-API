from logging import Formatter
import json
import traceback


class CustomFormatter(Formatter):
    """
    Formatter customizado para formatar mensagens de log.
    Esta classe herda de Formatter e sobrescreve o método format.
    """

    def __init__(self, datefmt="%Y-%m-%d %H:%M:%S", style="%"):
        log_format = "[%(asctime)s.%(msecs)03d] |%(levelname)s| - %(name)s: %(message)s"
        super().__init__(fmt=log_format, datefmt=datefmt, style=style)

    def format(self, record):
        super().format(record)

        log_data = {
            "timestamp": f"{record.asctime}.{record.msecs:03.0f}",
            "level": record.levelname,
            "filename": record.pathname,
            "function": record.funcName,
            "line": record.lineno,
            "module": record.module,
            "message": str(record.msg),
        }

        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            log_data["exception"] = {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "traceback": traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                ),
            }

        return json.dumps(log_data, ensure_ascii=False, indent=4)
