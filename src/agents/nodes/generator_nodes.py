from typing import Dict, Any
from src.agents.state import AgentState
from src.core.logger import get_logger

logger = get_logger(__name__)

def generate_post_node(state: AgentState) -> Dict[str, Any]:
    """Nodo placeholder para generar un post de LinkedIn."""
    logger.info("📝 Ejecutando nodo: generate_post_node (Generación de Post)")
    activos = dict(state.activos_generados)
    activos["linkedin_post"] = "Contenido de post generado (MOCK - Pendiente de implementar LLM)"
    return {"activos_generados": activos}

def generate_faq_node(state: AgentState) -> Dict[str, Any]:
    """Nodo placeholder para generar una respuesta para el FAQ."""
    logger.info("❓ Ejecutando nodo: generate_faq_node (Generación de FAQ)")
    activos = dict(state.activos_generados)
    activos["faq_entry"] = "Pregunta y respuesta FAQ generada (MOCK - Pendiente de implementar LLM)"
    return {"activos_generados": activos}

def generate_newsletter_node(state: AgentState) -> Dict[str, Any]:
    """Nodo placeholder para generar un extracto de Newsletter."""
    logger.info("📧 Ejecutando nodo: generate_newsletter_node (Generación de Newsletter)")
    activos = dict(state.activos_generados)
    activos["newsletter_snippet"] = "Extracto de newsletter generado (MOCK - Pendiente de implementar LLM)"
    return {"activos_generados": activos}
