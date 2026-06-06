import pytest
from unittest.mock import MagicMock, patch
from src.retrieval.rag_pipeline import VeterinaryRAGPipeline

def test_document_loader():
    pipeline = VeterinaryRAGPipeline()
    # Verificar que el loader se instancia correctamente
    assert pipeline.loader is not None
    
    # Cargar documentos reales en la carpeta raw
    docs = pipeline.loader.load()
    # Debe haber cargado los 16 documentos del corpus
    assert len(docs) > 0
    for doc in docs:
        assert "content" in doc
        assert "metadata" in doc
        assert doc["metadata"]["source_file"].endswith(".txt")

@patch("src.retrieval.rag_pipeline.VeterinaryRAGPipeline.retrieve_context")
def test_retrieve_context_mock(mock_retrieve):
    pipeline = VeterinaryRAGPipeline()
    
    mock_retrieve.return_value = [
        {
            "id": "doc_test_1",
            "content": "Vacuna contra parvovirus a las 6 semanas.",
            "metadata": {"source_file": "vacunacion_perros.txt", "section": "1. ESQUEMA"},
            "similarity": 0.95
        }
    ]
    
    results = pipeline.retrieve_context("¿Cuándo vacunar contra parvovirus?")
    assert len(results) == 1
    assert "parvovirus" in results[0]["content"]
    assert results[0]["metadata"]["source_file"] == "vacunacion_perros.txt"
