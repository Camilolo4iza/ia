import pytest
from src.ingestion.chunker import SectionChunker

def test_split_into_sections():
    chunker = SectionChunker()
    text = (
        "CARDIOLOGÍA VETERINARIA\n\n"
        "1. INTRODUCCIÓN\n"
        "Este es el texto de introducción sobre cardiología.\n\n"
        "2. TRATAMIENTO\n"
        "Este es el tratamiento recomendado para perros."
    )
    
    sections = chunker._split_into_sections(text)
    
    # Debe identificar al menos 2 secciones
    assert len(sections) >= 2
    assert any("INTRODUCCIÓN" in sec["title"] for sec in sections)
    assert any("TRATAMIENTO" in sec["title"] for sec in sections)

def test_split_document():
    chunker = SectionChunker(chunk_size=100, chunk_overlap=10)
    doc = {
        "content": (
            "1. VACUNACIÓN\n"
            "La vacunación es esencial para prevenir enfermedades virales en cachorros. "
            "Se debe iniciar a las 6 semanas de edad y continuar con refuerzos. "
            "Esto protege contra moquillo, parvovirus y leptospirosis."
        ),
        "metadata": {
            "source_file": "test.txt",
            "topic": "Test Topic"
        }
    }
    
    chunks = chunker.split_document(doc)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert "content" in chunk
        assert "metadata" in chunk
        assert chunk["metadata"]["source_file"] == "test.txt"
        assert chunk["metadata"]["topic"] == "Test Topic"
        assert "section" in chunk["metadata"]
