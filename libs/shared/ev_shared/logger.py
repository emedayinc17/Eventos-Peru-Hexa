
"""
ev_shared.logger
----------------
Logger simple con campos de contexto.
Synopsis: created by emeday 2025
"""
import logging, sys

def get_logger(name: str, service_name: str|None=None, **kwargs) -> logging.Logger:
    """
    Devuelve un logger configurado.
    Acepta argumentos extra (compatibilidad hacia atrás).
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = '%(asctime)s [%(levelname)s] [{}] %(name)s: %(message)s'.format(service_name or 'service')
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
