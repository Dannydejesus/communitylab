import logging
import sys
import os

def get_logger(name: str) -> logging.Logger:
    """
    Configura y devuelve un logger estandarizado para la aplicación.
    Cumple con los requerimientos de buenas prácticas y trazabilidad.
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicidad de handlers si el logger ya fue instanciado
    if logger.hasHandlers():
        return logger

    # Obtener el nivel de log desde variables de entorno (por defecto INFO)
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Formateador profesional: Fecha - Nombre - Nivel - Mensaje
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler opcional para archivo de errores persistente
    try:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/errores.log")
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback silencioso si no se puede escribir en disco
        pass

    return logger
