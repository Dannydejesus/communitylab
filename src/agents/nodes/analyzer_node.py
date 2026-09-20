import json
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_cohere import ChatCohere
from pydantic import ValidationError

from src.core.logger import get_logger
from src.core.exceptions import LLMConnectionError, DataValidationError
from src.agents.state import AgentState, InteractionAnalysis

logger = get_logger(__name__)

# Prompt base para el análisis cognitivo
ANALYSIS_PROMPT = """
Eres un analista experto en comunidades digitales (Community Manager AI).
Tu tarea es analizar el siguiente mensaje de un miembro de la comunidad y extraer:
1. Sentimiento general (Positivo, Negativo, Neutral, o Altamente Positivo).
2. Temas principales (ej. Contratacion, Dudas tecnicas, Logros, Feedback, etc.).
3. Puntuación de relevancia (0.0 a 10.0), donde 10 es un caso de éxito inspirador o una queja crítica.
4. Ruta sugerida (post_linkedin, faq, newsletter).

Mensaje:
{mensaje}

Formato de salida requerido (JSON exacto):
{format_instructions}
"""

def analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    Nodo de LangGraph que procesa todos los mensajes entrantes,
    realiza el análisis de sentimiento y categorización.
    """
    logger.info("Iniciando nodo de análisis (analyzer_node)...")
    
    # Configurar el parser para asegurar JSON de salida
    parser = JsonOutputParser(pydantic_object=InteractionAnalysis)
    
    prompt = ChatPromptTemplate.from_template(
        template=ANALYSIS_PROMPT,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # IMPORTANTE: Definir el LLM configurado para Cohere
    try:
        llm = ChatCohere(
            model="command-r-08-2024",
            temperature=0,
            cohere_api_key=os.getenv("COHERE_API_KEY")
        )
        chain = prompt | llm | parser
    except Exception as e:
        logger.error(f"Fallo al inicializar el LLM: {e}")
        raise LLMConnectionError(f"Error de inicialización del LLM: {e}")

    nuevos_analisis = {}
    errores = list(state.errores)

    for idx, interaccion in enumerate(state.interacciones):
        logger.info(f"Analizando interacción {idx+1}/{len(state.interacciones)} del autor '{interaccion.autor}'...")
        try:
            # Invocación al LLM
            resultado_json = chain.invoke({"mensaje": interaccion.texto})
            
            # Validación estricta con Pydantic
            analisis = InteractionAnalysis(**resultado_json)
            nuevos_analisis[idx] = analisis
            logger.info(f"✅ Análisis completado para interacción {idx+1}. Sentimiento: {analisis.sentimiento}")

        except ValidationError as ve:
            logger.error(f"❌ Error de validación Pydantic en interacción {idx+1}: {ve}")
            errores.append(f"Interacción {idx+1}: Formato de respuesta LLM inválido.")
        except Exception as e:
            logger.error(f"❌ Error al procesar interacción {idx+1} con el LLM: {e}")
            errores.append(f"Interacción {idx+1}: Error de LLM -> {str(e)}")

    logger.info("Finalizando nodo de análisis.")
    return {"analisis": nuevos_analisis, "errores": errores}
