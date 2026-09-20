from typing import Literal
from src.agents.state import AgentState
from src.core.logger import get_logger

logger = get_logger(__name__)

def router_function(state: AgentState) -> Literal["generate_post", "generate_faq", "generate_newsletter", "end"]:
    """
    Función de enrutamiento condicional para LangGraph.
    Decide el próximo nodo en función del campo 'ruta_sugerida'.
    """
    logger.info("🔀 Iniciando enrutamiento condicional...")
    
    if not state.analisis:
        logger.warning("No hay análisis para enrutar. Terminando.")
        return "end"
        
    # Para el MVP, tomamos el análisis de la primera interacción (índice 0)
    primer_analisis = state.analisis.get(0)
    if not primer_analisis:
        logger.warning("No se encontró el análisis con índice 0. Terminando.")
        return "end"
        
    ruta = primer_analisis.ruta_sugerida.lower().strip()
    logger.info(f"Ruta sugerida por el LLM detectada: '{ruta}'")
    
    # Lógica de bifurcación basada en palabras clave
    if "post" in ruta or "linkedin" in ruta:
        logger.info("➡️ Bifurcando hacia: generate_post")
        return "generate_post"
    elif "faq" in ruta:
        logger.info("➡️ Bifurcando hacia: generate_faq")
        return "generate_faq"
    elif "newsletter" in ruta:
        logger.info("➡️ Bifurcando hacia: generate_newsletter")
        return "generate_newsletter"
    else:
        logger.warning(f"Ruta '{ruta}' no reconocida. Terminando el flujo.")
        return "end"
