import re
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, START, END
from src.agents.state import VetAssistState
from src.agents.retriever_agent import RetrieverAgent
from src.agents.writer_agent import WriterAgent
from src.mcp.vet_mcp_server import calcular_dosis, consultar_vacunas
from src.retrieval.rag_pipeline import VeterinaryRAGPipeline


SUPPORTED_MEDICATIONS = ("meloxicam", "amoxicilina", "cefalexina", "metronidazol")

class VeterinaryAgentGraph:
    """
    Orquestador del flujo multiagente de VetAssist AI utilizando LangGraph.
    Coordina el ciclo de Retriever -> Writer con opción a bucle de retroalimentación
    si el Redactor determina que falta información crítica.
    """
    def __init__(self, rag_pipeline: VeterinaryRAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.graph = self._build_graph()

    def _build_graph(self):
        # Instanciar los agentes
        retriever = RetrieverAgent(self.rag_pipeline)
        writer = WriterAgent()

        # Inicializar el grafo con el estado compartido
        workflow = StateGraph(VetAssistState)

        # Agregar los nodos
        workflow.add_node("clinical_tools", self._run_clinical_tools)
        workflow.add_node("retriever_agent", retriever.run)
        workflow.add_node("writer_agent", writer.run)

        # Definir la estructura de aristas
        workflow.add_edge(START, "clinical_tools")
        workflow.add_edge("clinical_tools", "retriever_agent")
        workflow.add_edge("retriever_agent", "writer_agent")

        # Función de decisión condicional
        def decide_next_step(state: VetAssistState) -> str:
            # Si el redactor detecta información insuficiente y no hemos excedido el límite
            if state.get("missing_info", False) and state.get("loop_count", 0) < 2:
                print("[LangGraph Router] Arista condicional: Volviendo al Buscador...")
                return "retriever_agent"
            print("[LangGraph Router] Arista condicional: Finalizando flujo de agentes.")
            return "end"

        # Agregar la arista condicional
        workflow.add_conditional_edges(
            "writer_agent",
            decide_next_step,
            {
                "retriever_agent": "retriever_agent",
                "end": END
            }
        )

        # Compilar el grafo
        return workflow.compile()

    def _infer_age_weeks(self, patient_info: Dict[str, Any]) -> Optional[float]:
        if patient_info.get("edad_semanas"):
            return float(patient_info["edad_semanas"])

        edad_texto = str(patient_info.get("edad", "")).lower().replace(",", ".")
        match = re.search(r"(\d+(?:\.\d+)?)", edad_texto)
        if not match:
            return None

        value = float(match.group(1))
        if "año" in edad_texto or "ano" in edad_texto:
            return value * 52
        if "mes" in edad_texto:
            return value * 4.3
        if "sem" in edad_texto:
            return value
        return None

    def _run_clinical_tools(self, state: VetAssistState) -> Dict[str, List[str]]:
        query = state["query"].lower()
        patient_info = state.get("patient_info", {})
        outputs = []

        especie = str(patient_info.get("especie", "")).strip()
        peso = patient_info.get("peso")

        asks_for_dose = any(term in query for term in ("dosis", "dosificar", "dosificacion", "dosificación"))
        requested_meds = [med for med in SUPPORTED_MEDICATIONS if med in query]
        if asks_for_dose and requested_meds and peso and especie:
            for med in requested_meds:
                outputs.append(f"[Herramienta MCP: calcular_dosis]\n{calcular_dosis(med, float(peso), especie)}")

        asks_for_vaccines = any(term in query for term in ("vacuna", "vacunación", "vacunacion", "inmunización", "inmunizacion"))
        edad_semanas = self._infer_age_weeks(patient_info)
        if asks_for_vaccines and especie and edad_semanas is not None:
            outputs.append(f"[Herramienta MCP: consultar_vacunas]\n{consultar_vacunas(especie, edad_semanas)}")

        if outputs:
            print(f"[ClinicalTools] Se ejecutaron {len(outputs)} herramienta(s) MCP.")

        return {"tool_outputs": outputs}

    def ask(self, query: str, patient_info: Optional[Dict[str, Any]] = None) -> dict:
        """
        Ejecuta el grafo con la consulta del usuario.
        """
        initial_state = {
            "query": query,
            "retrieved_docs": [],
            "answer": "",
            "sources": [],
            "loop_count": 0,
            "missing_info": False,
            "missing_feedback": "",
            "tool_outputs": [],
            "patient_info": patient_info or {}
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            return {
                "query": query,
                "answer": final_state.get("answer", ""),
                "sources": final_state.get("sources", []),
                "tool_outputs": final_state.get("tool_outputs", []),
                "docs_retrieved_count": len(final_state.get("retrieved_docs", []))
            }
        except Exception as e:
            return {
                "query": query,
                "answer": f"⚠️ Error en la ejecución del orquestador de agentes: {str(e)}",
                "sources": [],
                "tool_outputs": [],
                "docs_retrieved_count": 0
            }
