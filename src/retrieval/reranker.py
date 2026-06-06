from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
from src.config import RERANKER_MODEL, RAG_TOP_K_RERANK

class VeterinaryReranker:
    """
    Realiza un re-ranking secundario de los fragmentos recuperados utilizando un modelo Cross-Encoder.
    Esto mejora sustancialmente la precisión del contexto inyectado al LLM.
    """
    def __init__(self, model_name: str = RERANKER_MODEL):
        self.model_name = model_name
        # Cargamos el modelo Cross-Encoder (se descarga/carga localmente)
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = RAG_TOP_K_RERANK) -> List[Dict[str, Any]]:
        """
        Somete una lista de documentos candidatos a re-ranking contra la consulta original.
        Retorna los mejores top_k documentos ordenados de forma descendente por relevancia.
        """
        if not documents:
            return []

        # Crear los pares (query, document_content)
        pairs = [[query, doc["content"]] for doc in documents]
        
        # Calcular los scores
        scores = self.model.predict(pairs)
        
        # Asignar scores a los documentos
        for i, score in enumerate(scores):
            documents[i]["rerank_score"] = float(score)
            
        # Ordenar descendente por el score obtenido
        sorted_documents = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        
        # Retornar los top_k resultados
        return sorted_documents[:top_k]
