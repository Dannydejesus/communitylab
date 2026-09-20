from langgraph.graph import StateGraph, START, END
from src.agents.state import AgentState
from src.agents.nodes.analyzer_node import analyzer_node
from src.agents.nodes.router_node import router_function
from src.agents.nodes.generator_nodes import generate_post_node, generate_faq_node, generate_newsletter_node
from src.core.logger import get_logger

logger = get_logger(__name__)

def create_graph():
    """
    Ensambla y compila el grafo principal de LangGraph para el Motor Inteligente.
    Define el flujo de ejecución de los agentes.
    """
    logger.info("Ensamblando el grafo de LangGraph...")
    
    try:
        # Inicializar el grafo con el esquema de estado global
        workflow = StateGraph(AgentState)
        
        # 1. Añadir nodos (workers)
        workflow.add_node("analyzer", analyzer_node)
        workflow.add_node("generate_post", generate_post_node)
        workflow.add_node("generate_faq", generate_faq_node)
        workflow.add_node("generate_newsletter", generate_newsletter_node)
        
        # 2. Definir las conexiones estáticas (edges iniciales)
        workflow.add_edge(START, "analyzer")
        
        # 3. Definir conexiones dinámicas (conditional edges desde el analyzer)
        workflow.add_conditional_edges(
            "analyzer", 
            router_function,
            {
                "generate_post": "generate_post",
                "generate_faq": "generate_faq",
                "generate_newsletter": "generate_newsletter",
                "end": END
            }
        )
        
        # 4. Todos los nodos generadores terminan el flujo en esta iteración del MVP
        workflow.add_edge("generate_post", END)
        workflow.add_edge("generate_faq", END)
        workflow.add_edge("generate_newsletter", END)
        
        # 5. Compilar el grafo
        compiled_graph = workflow.compile()
        logger.info("✅ Grafo ensamblado y compilado correctamente con enrutamiento.")
        
        return compiled_graph
        
    except Exception as e:
        logger.error(f"❌ Error crítico al ensamblar el grafo: {e}")
        raise

# Instancia global del grafo lista para ser invocada
app_graph = create_graph()
