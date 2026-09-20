class MotorInteligenteError(Exception):
    """Clase base para excepciones personalizadas del Motor Inteligente."""
    pass

class LLMConnectionError(MotorInteligenteError):
    """Error al comunicarse con la API del LLM (ej. error de red o timeout)."""
    pass

class DataValidationError(MotorInteligenteError):
    """Error cuando los datos de entrada o salida no cumplen con el esquema Pydantic."""
    pass

class ContentGenerationError(MotorInteligenteError):
    """Error durante la fase de generación de contenido multicanal."""
    pass
