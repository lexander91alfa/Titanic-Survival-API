from logging import FileHandler, Logger, StreamHandler, getLogger
from logging import INFO
from src.logging.custom_formatter import CustomFormatter
from uuid import uuid4
from os import path, makedirs
from datetime import datetime


def get_logger(type_logger="console", level=INFO) -> Logger:
    """
    Cria um logger configurado com um manipulador de arquivo e um formatador customizado.
    O logger é configurado para registrar mensagens de nível INFO e superior.
    Se o tipo de logger for 'console', o logger será configurado para registrar mensagens
    no console. Caso contrário, o logger será configurado para registrar mensagens em um
    arquivo chamado 'app.log' na pasta 'logs'.
    Se a pasta 'logs' não existir, ela será criada automaticamente.
    O logger é identificado por um UUID único gerado a cada chamada da função.
    O logger é configurado para sempre incluir informações de exceção (exc_info=True) nas mensagens de erro,
    exceção e críticas.

    Args:
        type_logger (str): Tipo de logger ('console' ou 'file'). Se None ou não especificado,
            o logger será configurado apenas para arquivo.
        level (int): Nível de log. O padrão é INFO.
            Outros níveis disponíveis incluem DEBUG, WARNING, ERROR e CRITICAL.

    Returns:
        logging.Logger: Instância do logger configurado.
    """
    formatter = CustomFormatter()
    logger = getLogger(str(uuid4()))
    
    logger.propagate = False
    
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.propagate = False

    if type_logger == "console":
        handler = StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    else:
        if not path.exists("./logs"):
            makedirs("./logs")

        filename = f"./logs/app_{datetime.now().strftime('%Y-%m-%d')}.log"

        handler = FileHandler(filename=filename, encoding="utf-8")
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
