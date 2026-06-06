import os
from typing import List, Dict, Any, Tuple
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    SYSTEM_PROMPT_WRITER,
    RAG_TOP_K_RETRIEVAL,
    RAG_TOP_K_RERANK
)
from src.ingestion.loader import DocumentLoader
from src.ingestion.chunker import SectionChunker
from src.ingestion.embedder import VectorEmbedder
from src.retrieval.vector_store import VeterinaryVectorStore
from src.retrieval.reranker import VeterinaryReranker


class VeterinaryRAGPipeline:
    """
    Pipeline RAG (Retrieval-Augmented Generation) para VetAssist AI.
    Coordina la ingesta, recuperación, re-ranking y generación final de respuestas.
    """
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = SectionChunker()
        
        # Inicialización diferida de modelos pesados para optimizar memoria en cargas ligeras
        self._embedder = None
        self._vector_store = None
        self._reranker = None
        self._llm = None

    @property
    def embedder(self) -> VectorEmbedder:
        if self._embedder is None:
            self._embedder = VectorEmbedder()
        return self._embedder

    @property
    def vector_store(self) -> VeterinaryVectorStore:
        if self._vector_store is None:
            self._vector_store = VeterinaryVectorStore()
        return self._vector_store

    @property
    def reranker(self) -> VeterinaryReranker:
        if self._reranker is None:
            self._reranker = VeterinaryReranker()
        return self._reranker

    @property
    def llm(self) -> ChatGroq:
        if self._llm is None:
            if not GROQ_API_KEY:
                raise ValueError(
                    "Falta la clave API de Groq. Por favor, crea un archivo .env en la raíz del "
                    "proyecto y define GROQ_API_KEY=tu_clave_aquí."
                )
            self._llm = ChatGroq(
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                api_key=GROQ_API_KEY
            )
        return self._llm

    def ingest(self, force: bool = False) -> Dict[str, Any]:
        """
        Carga e ingesta los documentos raw en la base de datos vectorial.
        """
        stats = self.vector_store.get_stats()
        if stats["total_chunks"] > 0 and not force:
            return {
                "status": "skipped",
                "message": "La base vectorial ya contiene datos. Usa force=True para re-ingestar.",
                "stats": stats
            }

        if force:
            self.vector_store.reset_collection()

        print("Iniciando ingesta de documentos veterinarios...")
        docs = self.loader.load()
        if not docs:
            return {
                "status": "error",
                "message": "No se encontraron documentos para ingestar en la carpeta data/raw."
            }

        # Fragmentar documentos
        all_chunks = []
        for doc in docs:
            chunks = self.chunker.split_document(doc)
            all_chunks.extend(chunks)

        print(f"Documentos cargados: {len(docs)}, fragmentados en {len(all_chunks)} chunks.")

        # Obtener los textos para generar embeddings
        chunk_texts = [chunk["content"] for chunk in all_chunks]
        
        # Generar embeddings
        print("Generando embeddings (sentence-transformers)...")
        embeddings = self.embedder.embed_documents(chunk_texts)

        # Guardar en ChromaDB
        print("Guardando chunks en ChromaDB...")
        self.vector_store.add_chunks(all_chunks, embeddings)

        updated_stats = self.vector_store.get_stats()
        print("¡Ingesta completada con éxito!")
        return {
            "status": "success",
            "message": f"Se ingestaron {len(docs)} documentos en {len(all_chunks)} fragmentos.",
            "stats": updated_stats
        }

    def retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Recupera el contexto relevante realizando búsqueda vectorial y re-ranking.
        """
        # 1. Obtener embedding de la query
        query_emb = self.embedder.embed_query(query)
        
        # 2. Búsqueda inicial en ChromaDB (top 10)
        initial_results = self.vector_store.query(query_emb, top_k=RAG_TOP_K_RETRIEVAL)
        if not initial_results:
            return []

        # 3. Aplicar re-ranking semántico con Cross-Encoder (top 3)
        reranked_results = self.reranker.rerank(query, initial_results, top_k=RAG_TOP_K_RERANK)
        return reranked_results

    def format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Formatea los fragmentos recuperados para inyectarlos en el prompt.
        """
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            source = doc["metadata"]["source_file"]
            section = doc["metadata"]["section"]
            similarity = doc.get("rerank_score", doc.get("similarity", 0.0))
            
            context_parts.append(
                f"--- DOCUMENTO CANDIDATO {i+1} ---\n"
                f"Archivo Origen: {source}\n"
                f"Sección: {section}\n"
                f"Score de Relevancia: {similarity:.4f}\n"
                f"Contenido:\n{doc['content']}\n"
            )
        return "\n".join(context_parts)

    def answer(self, query: str) -> Dict[str, Any]:
        """
        Responde a la pregunta del usuario utilizando el pipeline RAG.
        """
        try:
            # 1. Recuperar contexto relevante
            context_docs = self.retrieve_context(query)
            
            if not context_docs:
                return {
                    "query": query,
                    "answer": "Lo siento, no tengo información en mi base de conocimientos para responder a esa pregunta.",
                    "context": [],
                    "sources": []
                }

            # 2. Formatear el contexto
            formatted_context = self.format_context(context_docs)
            
            # 3. Construir el prompt de sistema y de usuario
            system_msg = SystemMessage(content=SYSTEM_PROMPT_WRITER)
            
            user_prompt = (
                f"Pregunta del usuario:\n{query}\n\n"
                f"Contexto recuperado de la base de conocimiento veterinario:\n"
                f"{formatted_context}\n\n"
                f"Redacta una respuesta basada únicamente en el contexto provisto."
            )
            user_msg = HumanMessage(content=user_prompt)

            # 4. Generar respuesta con el LLM
            response = self.llm.invoke([system_msg, user_msg])
            
            # 5. Extraer fuentes únicas
            sources = list(set([doc["metadata"]["source_file"] for doc in context_docs]))
            
            return {
                "query": query,
                "answer": response.content,
                "context": context_docs,
                "sources": sources
            }
            
        except Exception as e:
            # Retorno amigable en caso de error de API o configuración
            return {
                "query": query,
                "answer": f"⚠️ Ocurrió un error al procesar tu consulta: {str(e)}",
                "context": [],
                "sources": []
            }
