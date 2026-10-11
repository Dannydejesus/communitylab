"""Cliente compartido de Gemini con inicialización diferida."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI


MODELO_GEMINI = "gemini-3.5-flash-lite"
# Bajo a propósito: los reintentos de la aplicación (reintentos.py) se suman a estos.
MAX_RETRIES_GEMINI = 2
INTERVALO_REVISION_LIMITADOR = 0.1
TAMANO_MAXIMO_LIMITADOR = 1

# Límite observado en Gemini Free Tier:
# 15 requests por minuto para este modelo.
#
# Trabajamos a ~12 RPM para dejar margen.
SOLICITUDES_POR_SEGUNDO = 0.20


def obtener_configuracion_modelo() -> dict[str, str | int | float]:
    """Devuelve los parámetros no secretos usados en las llamadas a Gemini."""
    return {
        "proveedor": "Google Gemini",
        "identificador_modelo": MODELO_GEMINI,
        "max_retries": MAX_RETRIES_GEMINI,
        "solicitudes_por_segundo": SOLICITUDES_POR_SEGUNDO,
        "intervalo_revision_limitador_segundos": INTERVALO_REVISION_LIMITADOR,
        "tamano_maximo_limitador": TAMANO_MAXIMO_LIMITADOR,
    }

_rate_limiter = InMemoryRateLimiter(
    requests_per_second=SOLICITUDES_POR_SEGUNDO,
    check_every_n_seconds=INTERVALO_REVISION_LIMITADOR,
    max_bucket_size=TAMANO_MAXIMO_LIMITADOR,
)


@lru_cache(maxsize=1)
def obtener_modelo_gemini():
    """
    Carga las credenciales y crea el cliente del LLM según la prioridad:
    1. NVIDIA NIM (Nemotron) como motor principal.
    2. Cohere (Command-R) como respaldo activo.
    3. Gemini como proveedor alternativo.
    """
    load_dotenv()

    nvidia_key = os.getenv("NVIDIA_API_KEY")
    cohere_key = os.getenv("COHERE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    # 1. Prioridad: NVIDIA NIM (Nemotron)
    if nvidia_key:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=nvidia_key,
                model="nvidia/nemotron-3.5-lightning-30b-a3b",
                temperature=0.1,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            )
        except Exception:
            pass

    # 2. Respaldo (Fallback): Cohere
    if cohere_key:
        try:
            from langchain_cohere import ChatCohere
            return ChatCohere(
                model="command-r-08-2024",
                cohere_api_key=cohere_key,
                temperature=0.1,
            )
        except Exception:
            pass

    # 3. Gemini si está disponible
    if gemini_key:
        return ChatGoogleGenerativeAI(
            api_key=gemini_key,
            model=MODELO_GEMINI,
            rate_limiter=_rate_limiter,
            max_retries=MAX_RETRIES_GEMINI,
        )

    raise ValueError(
        "No se encontró NVIDIA_API_KEY, COHERE_API_KEY ni GEMINI_API_KEY en el archivo .env."
    )