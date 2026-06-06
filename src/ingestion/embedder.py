from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from src.config import EMBEDDING_MODEL

class VectorEmbedder:
    """
    Genera embeddings utilizando sentence-transformers localmente.
    """
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> List[float]:
        """
        Genera el embedding para una consulta de texto.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de documentos.
        """
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()
