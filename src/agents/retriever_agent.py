from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import GROQ_API_KEY, LLM_MODEL, SYSTEM_PROMPT_RETRIEVER
from src.retrieval.rag_pipeline import VeterinaryRAGPipeline

class RetrieverAgent:
    """
    Agente Buscador. Analiza la consulta, la reformula si es necesario para
    optimizar la búsqueda semántica, y recupera documentos relevantes de la base vectorial.
    """
    def __init__(self, rag_pipeline: VeterinaryRAGPipeline):
        self.rag_pipeline = rag_pipeline
        self._llm = None

    @property
    def llm(self) -> ChatGroq:
        if self._llm is None:
            self._llm = ChatGroq(
                model=LLM_MODEL,
                temperature=0.1,  # Baja temperatura para consistencia
                api_key=GROQ_API_KEY
            )
        return self._llm

    def reformulate_query(self, original_query: str, feedback: str = "") -> str:
        """
        Usa el LLM para optimizar o reformular la consulta del usuario.
        Si se provee feedback (ej. información faltante), se enfoca en ese aspecto.
        """
        try:
            system_msg = SystemMessage(content=SYSTEM_PROMPT_RETRIEVER)
            
            prompt = f"Consulta original: {original_query}\n"
            if feedback:
                prompt += f"Búsqueda anterior incompleta. Enfócate en recuperar información sobre: {feedback}\n"
            
            prompt += (
                "\nGenera una única frase optimizada para la búsqueda semántica en español. "
                "No agregues explicaciones, devuelve únicamente la consulta reformulada."
            )
            
            user_msg = HumanMessage(content=prompt)
            response = self.llm.invoke([system_msg, user_msg])
            reformulated = response.content.strip().strip('"')
            return reformulated
        except Exception as e:
            print(f"Error al reformular consulta: {str(e)}. Usando la consulta original.")
            return original_query

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nodo ejecutor del agente dentro de LangGraph.
        """
        query = state["query"]
        loop_count = state.get("loop_count", 0)
        
        # Si ya hemos iterado y hay missing_info, reformulamos con enfoque en el feedback
        feedback = ""
        if loop_count > 0 and state.get("missing_info", False):
            feedback = state.get("missing_feedback") or state.get("answer", "")
            
        print(f"[{self.__class__.__name__}] Analizando consulta: '{query}'")
        search_query = self.reformulate_query(query, feedback)
        print(f"[{self.__class__.__name__}] Consulta optimizada de búsqueda: '{search_query}'")

        # Recuperar documentos relevantes
        context_docs = self.rag_pipeline.retrieve_context(search_query)
        print(f"[{self.__class__.__name__}] Se recuperaron {len(context_docs)} fragmentos relevantes.")

        # Retornamos el estado actualizado
        # retrieved_docs se sumará automáticamente gracias al Annotator `operator.add`
        return {
            "retrieved_docs": context_docs,
            "loop_count": loop_count + 1
        }
