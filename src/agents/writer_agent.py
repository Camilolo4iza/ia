from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import GROQ_API_KEY, LLM_MODEL, SYSTEM_PROMPT_WRITER, DISCLAIMER

class WriterAgent:
    """
    Agente Redactor. Recibe los documentos recuperados por el Buscador,
    evalúa si la información es suficiente, y redacta la respuesta final
    con un tono veterinario profesional, citando fuentes e insertando el disclaimer.
    """
    def __init__(self):
        self._llm = None

    @property
    def llm(self) -> ChatGroq:
        if self._llm is None:
            self._llm = ChatGroq(
                model=LLM_MODEL,
                temperature=0.3,
                api_key=GROQ_API_KEY
            )
        return self._llm

    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Da formato legible a los documentos acumulados en el estado."""
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            source = doc.get("metadata", {}).get("source_file", "desconocido")
            section = doc.get("metadata", {}).get("section", "general")
            content = doc.get("content", "")
            context_parts.append(
                f"Documento [{i+1}] (Origen: {source} | Sección: {section}):\n{content}\n"
            )
        return "\n".join(context_parts)

    def _format_tool_outputs(self, tool_outputs: List[str]) -> str:
        """Da formato legible a los resultados de herramientas MCP."""
        if not tool_outputs:
            return ""
        return "\n\n".join(tool_outputs)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nodo ejecutor del agente dentro de LangGraph.
        """
        query = state["query"]
        docs = state.get("retrieved_docs", [])
        tool_outputs = state.get("tool_outputs", [])
        loop_count = state.get("loop_count", 0)

        print(
            f"[{self.__class__.__name__}] Redactando respuesta con "
            f"{len(docs)} documentos y {len(tool_outputs)} salida(s) de herramientas..."
        )

        if not docs and not tool_outputs:
            return {
                "answer": "Lo siento, no he podido encontrar información relevante en mi base de datos.",
                "missing_info": False,
                "missing_feedback": "",
                "sources": []
            }

        formatted_context = self._format_context(docs)
        formatted_tools = self._format_tool_outputs(tool_outputs)
        complete_context = "\n\n".join(
            part for part in [
                f"Resultados de herramientas clínicas MCP:\n{formatted_tools}" if formatted_tools else "",
                f"Documentos recuperados del corpus:\n{formatted_context}" if formatted_context else "",
            ]
            if part
        )

        # Prompt de validación e informe
        eval_prompt = (
            f"Consulta del usuario:\n{query}\n\n"
            f"Contexto disponible:\n{complete_context}\n\n"
            f"Instrucciones de evaluación:\n"
            f"1. Si el contexto provisto NO contiene información relevante o suficiente para responder a la consulta, "
            f"responde exactamente comenzando con el tag '[INFORMACION_INSUFICIENTE]' seguido de una breve explicación de qué falta.\n"
            f"2. Si la información es suficiente, responde con la respuesta veterinaria completa y profesional.\n"
            f"3. Puedes usar resultados MCP para dosis y calendarios; cítalos como [Fuente: MCP calcular_dosis] "
            f"o [Fuente: MCP consultar_vacunas] según corresponda.\n"
            f"4. Sigue estrictamente las reglas del agente redactor (citar fuentes como [Fuente: nombre_archivo], "
            f"usar tono profesional en español, no inventar datos y recordar la advertencia médica).\n"
        )

        try:
            system_msg = SystemMessage(content=SYSTEM_PROMPT_WRITER)
            user_msg = HumanMessage(content=eval_prompt)
            
            response = self.llm.invoke([system_msg, user_msg])
            response_text = response.content.strip()
            
            # Verificar si se activó el tag de información insuficiente
            if response_text.startswith("[INFORMACION_INSUFICIENTE]") and loop_count < 2:
                print(f"[{self.__class__.__name__}] Se detectó información insuficiente. Solicitando segunda búsqueda...")
                feedback = response_text.replace("[INFORMACION_INSUFICIENTE]", "").strip()
                return {
                    "missing_info": True,
                    "missing_feedback": feedback,
                    "answer": response_text
                }
            
            # Limpiar tag de información insuficiente si excedió el número de bucles
            if response_text.startswith("[INFORMACION_INSUFICIENTE]"):
                response_text = (
                    "Nota: La base de datos contiene información limitada sobre este tema particular. "
                    "A continuación presento la información disponible:\n\n" + 
                    response_text.replace("[INFORMACION_INSUFICIENTE]", "").strip()
                )

            # Agregar el Disclaimer si no está presente en la respuesta del LLM
            if "Aviso importante" not in response_text and "disclaimer" not in response_text.lower():
                response_text += f"\n\n{DISCLAIMER}"

            # Extraer fuentes únicas del contexto
            sources = list(set([doc["metadata"]["source_file"] for doc in docs]))
            if tool_outputs:
                sources.append("MCP herramientas clínicas")

            return {
                "answer": response_text,
                "missing_info": False,
                "missing_feedback": "",
                "sources": sources
            }

        except Exception as e:
            return {
                "answer": f"⚠️ Error en la redacción de la respuesta: {str(e)}",
                "missing_info": False,
                "missing_feedback": "",
                "sources": []
            }
