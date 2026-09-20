from typing import Annotated, Dict, Any, List, Optional
from pydantic import BaseModel, Field
import operator

class InteractionData(BaseModel):
    """Estructura de un mensaje individual de la comunidad."""
    autor: str = Field(description="Nombre del autor del mensaje")
    canal: str = Field(description="Canal de origen (ej. #dudas)")
    tipo: str = Field(description="Tipo de interacción (ej. testimonio, duda)")
    texto: str = Field(description="Contenido en texto crudo del mensaje")

class InteractionAnalysis(BaseModel):
    """Resultado del análisis cognitivo realizado por el LLM."""
    sentimiento: str = Field(description="Sentimiento (ej. Positivo, Negativo, Neutral)")
    temas: List[str] = Field(description="Lista de temas extraídos")
    puntuacion_relevancia: float = Field(default=0.0, description="Score de relevancia del 0 al 10")
    ruta_sugerida: str = Field(description="Ruta de bifurcación (ej. post, faq)")

class AgentState(BaseModel):
    """
    Estado global del grafo de LangGraph. 
    Contiene la información de entrada, estado intermedio y resultados.
    """
    origen_comunidad: str = Field(default="")
    periodo_referencia: str = Field(default="")
    
    # Lista de mensajes de entrada
    interacciones: List[InteractionData] = Field(default_factory=list)
    
    # Resultados intermedios (diccionario mapeando índice de mensaje a análisis)
    analisis: Dict[int, InteractionAnalysis] = Field(default_factory=dict)
    
    # Resultados finales
    activos_generados: Dict[str, Any] = Field(default_factory=dict)
    errores: List[str] = Field(default_factory=list)
