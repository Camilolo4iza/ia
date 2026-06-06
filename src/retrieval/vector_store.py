import chromadb
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

class VeterinaryVectorStore:
    """
    Controlador para ChromaDB local persistente.
    Gestiona la inserción y búsqueda de fragmentos con embeddings.
    """
    def __init__(self, persist_dir: Path = CHROMA_PERSIST_DIR, collection_name: str = CHROMA_COLLECTION_NAME):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        # Usamos distancia coseno para la similitud semántica
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Agrega fragmentos (chunks) y sus correspondientes embeddings a la base vectorial.
        """
        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            # Generar un ID único por fragmento
            source = chunk["metadata"]["source_file"].replace(".", "_")
            idx = chunk["metadata"]["chunk_index"]
            ids.append(f"doc_{source}_{idx}")
            
            documents.append(chunk["content"])
            
            # Asegurarse de que los valores de metadatos sean de tipos válidos para ChromaDB
            meta = {
                "source_file": chunk["metadata"]["source_file"],
                "topic": chunk["metadata"]["topic"],
                "section": chunk["metadata"]["section"],
                "chunk_index": idx
            }
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda de similitud utilizando el embedding de la consulta.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        if not results or "documents" not in results or not results["documents"][0]:
            return formatted_results

        # Extraer y formatear resultados
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        ids = results["ids"][0]

        for i in range(len(docs)):
            # Distancia coseno: menor distancia = mayor similitud. 
            # Convertimos a score de similitud (1 - distancia)
            score = 1.0 - distances[i]
            formatted_results.append({
                "id": ids[i],
                "content": docs[i],
                "metadata": metas[i],
                "similarity": float(score)
            })
            
        return formatted_results

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas básicas de la colección.
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "persist_directory": str(self.persist_dir)
        }

    def reset_collection(self):
        """
        Elimina y recrea la colección actual.
        """
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
