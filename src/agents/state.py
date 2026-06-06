from typing import List, Dict, Any, TypedDict, Annotated
import operator

class VetAssistState(TypedDict):
    """
    Estado compartido que fluye a través del grafo LangGraph.
    """
    # Consulta original del usuario
    query: str
    
    # Documentos recuperados acumulados (usamos operator.add para agregarlos dinámicamente)
    retrieved_docs: Annotated[List[Dict[str, Any]], operator.add]
    
    # Respuesta final redactada
    answer: str
    
    # Fuentes únicas consultadas
    sources: List[str]
    
    # Contador de iteraciones para evitar bucles infinitos
    loop_count: int
    
    # Flag para indicar si hace falta información adicional
    missing_info: bool

    # Retroalimentación concreta del redactor para una segunda búsqueda
    missing_feedback: str
    
    # Campos opcionales para la ejecución de herramientas (MCP)
    tool_outputs: List[str]

    # Datos clínicos del paciente aportados por la interfaz
    patient_info: Dict[str, Any]
