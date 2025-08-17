
import logging
import sys

_LOGGER_INITIALIZED = False

def _init_logging():
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    _LOGGER_INITIALIZED = True

def get_app_logger(name: str) -> logging.Logger:
    _init_logging()
    logger = logging.getLogger(name)
    return logger
