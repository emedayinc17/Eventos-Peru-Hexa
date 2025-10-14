# created by emeday 2025
# Logging simple y consistente entre servicios. Sin dependencias externas.
import logging
import os
from typing import Optional

_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def get_logger(name: str, service_name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(_LEVEL)
    if not logger.handlers:
        ch = logging.StreamHandler()
        fmt = "[%(asctime)s] [%(levelname)s]"
        if service_name:
            fmt += f" [{service_name}]"
        fmt += " %(name)s: %(message)s"
        ch.setFormatter(logging.Formatter(fmt))
        logger.addHandler(ch)
        logger.propagate = False
    return logger
