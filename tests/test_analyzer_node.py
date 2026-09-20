import json
import os
from unittest.mock import patch
from langchain_core.messages import AIMessage
from src.agents.state import AgentState, InteractionData
from src.agents.nodes.analyzer_node import analyzer_node

# Configurar variable de entorno dummy para el test para que ChatCohere no falle al instanciarse
os.environ["COHERE_API_KEY"] = "dummy_key_for_testing"

def test_analyzer_node_success():
    """Verifica el procesamiento exitoso del nodo de análisis sin llamar a la API real."""
    estado = AgentState(
        interacciones=[
            InteractionData(
                autor="TestUser", 
                canal="#general", 
                tipo="duda", 
                texto="Este es un mensaje de prueba para unit test."
            )
        ]
    )
    
    mock_dict = {
        "sentimiento": "Positivo",
        "temas": ["Pruebas unitarias"],
        "puntuacion_relevancia": 7.5,
        "ruta_sugerida": "faq"
    }
    
    # Simular la respuesta del modelo Cohere devolviendo el JSON como string
    # El JsonOutputParser se encargará de convertir este string en un dict
    mock_ai_message = AIMessage(content=json.dumps(mock_dict))
    
    # Parcheamos el método invoke de ChatCohere
    with patch("langchain_cohere.ChatCohere.invoke", return_value=mock_ai_message):
        resultado = analyzer_node(estado)
        
    # Verificaciones asertivas
    assert "analisis" in resultado
    assert "errores" in resultado
    assert len(resultado["errores"]) == 0
    assert 0 in resultado["analisis"]
    
    analisis = resultado["analisis"][0]
    assert analisis.sentimiento == "Positivo"
    assert analisis.ruta_sugerida == "faq"
    assert "Pruebas unitarias" in analisis.temas
