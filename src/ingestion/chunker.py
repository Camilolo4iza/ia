import re
import tiktoken
from typing import List, Dict, Any
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

class SectionChunker:
    """
    Divide documentos en fragmentos (chunks) estructurados por secciones
    para preservar el contexto semántico de títulos y temas.
    """
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None

    def _count_tokens(self, text: str) -> int:
        """Cuenta tokens de un texto."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Estimación básica si no hay tokenizador (1 palabra ~ 1.3 tokens)
        return int(len(text.split()) * 1.3)

    def _split_into_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Divide el documento en secciones basadas en encabezados.
        Busca patrones comunes de títulos como:
        - I. INTRODUCCIÓN
        - 1. INTRODUCCIÓN
        - INTRODUCCIÓN (en mayúsculas)
        """
        lines = content.split("\n")
        sections = []
        current_section_title = "General"
        current_section_content = []

        # Expresión regular para detectar títulos de secciones (ej: "1. INTRODUCCIÓN" o "INTRODUCCIÓN")
        section_pattern = re.compile(r"^(?:(?:[0-9]+|[A-Z]+)\.\s+|[IVXLCDM]+\.\s+)?([A-ZÁÉÍÓÚÑ\s]{3,50})$")

        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue

            # Verificar si es una línea de título
            match = section_pattern.match(line_strip)
            # Evitamos falsos positivos para líneas cortas que no son títulos
            if match and len(line_strip) < 60 and not line_strip.endswith((".", ",", ";", ":")):
                # Si ya teníamos contenido en la sección anterior, la guardamos
                if current_section_content:
                    sections.append({
                        "title": current_section_title,
                        "content": "\n".join(current_section_content)
                    })
                current_section_title = line_strip
                current_section_content = []
            else:
                current_section_content.append(line)

        # Añadir la última sección
        if current_section_content:
            sections.append({
                "title": current_section_title,
                "content": "\n".join(current_section_content)
            })

        # Si no se detectaron secciones, devolver el documento completo como una sección "General"
        if not sections:
            sections = [{"title": "General", "content": content}]

        return sections

    def split_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fragmenta un documento en chunks y les asocia metadatos enriquecidos.
        """
        content = doc["content"]
        metadata = doc["metadata"]
        
        sections = self._split_into_sections(content)
        chunks = []

        for section in sections:
            sec_title = section["title"]
            sec_content = section["content"]
            
            # Preparamos el contexto que irá embebido en el texto de cada chunk
            context_header = f"[Documento: {metadata['source_file']} | Tema: {metadata['topic']} | Sección: {sec_title}]\n"
            header_tokens = self._count_tokens(context_header)
            
            # El espacio restante para el contenido real del chunk
            available_size = self.chunk_size - header_tokens
            if available_size <= 50: # Evitar chunks ridículamente pequeños
                available_size = self.chunk_size
                context_header = ""
                header_tokens = 0
            
            # Dividimos por palabras
            words = sec_content.split(" ")
            current_words = []
            current_tokens = 0
            
            i = 0
            while i < len(words):
                word = words[i]
                word_tokens = self._count_tokens(word + " ")
                
                # Si una sola palabra excede el espacio disponible (raro), la forzamos
                if word_tokens > available_size and current_tokens == 0:
                    current_words.append(word)
                    i += 1
                    break
                
                if current_tokens + word_tokens <= available_size:
                    current_words.append(word)
                    current_tokens += word_tokens
                    i += 1
                else:
                    # Crear el fragmento
                    chunk_text = context_header + " ".join(current_words)
                    chunks.append({
                        "content": chunk_text,
                        "metadata": {
                            **metadata,
                            "section": sec_title,
                            "tokens": current_tokens + header_tokens,
                            "chunk_index": len(chunks)
                        }
                    })
                    
                    # Implementar solapamiento (overlap) retrocediendo palabras
                    # Retrocedemos aproximadamente la mitad del overlap
                    overlap_words_target = max(1, int(len(current_words) * (self.chunk_overlap / self.chunk_size)))
                    current_words = current_words[-overlap_words_target:] if overlap_words_target < len(current_words) else []
                    current_tokens = self._count_tokens(" ".join(current_words))
            
            # Guardar el último fragmento de la sección si tiene contenido
            if current_words:
                chunk_text = context_header + " ".join(current_words)
                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        **metadata,
                        "section": sec_title,
                        "tokens": current_tokens + header_tokens,
                        "chunk_index": len(chunks)
                    }
                })

        return chunks
