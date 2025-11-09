import datetime
import logging

from src.config.config import config
from src.helpers.datetime import get_timestamp


def get_logger(filename):
    # Formato do nome do arquivo de log
    log_filename = datetime.datetime.now().strftime(
        f"{config["LOG_DIRECTORY"]}/{filename}_%Y%m%d_%H%M%S.log"
    )

    # Configuração do logging
    logging.basicConfig(
        filename=log_filename,  # Nome do arquivo de log
        level=logging.INFO,  # Nível mínimo de log
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Criar e retornar o logger
    logger = logging.getLogger()
    return logger


def print_logger(logger, type, message):
    print(f"{get_timestamp()} - {message.rstrip()}")
    if type == "info":
        logger.info(message)
    elif type == "error":
        logger.error(message)
