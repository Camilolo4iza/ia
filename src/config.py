"""
Configuración centralizada de VetAssist AI.

Contiene todas las constantes, rutas y parámetros del sistema.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ==============================================
# Rutas del proyecto
# ==============================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHROMA_PERSIST_DIR = PROCESSED_DATA_DIR / "chroma"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Crear directorios si no existen
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CHROMA_PERSIST_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==============================================
# LLM Configuration (Groq + Llama 3.3)
# ==============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2048

# ==============================================
# Embeddings Configuration
# ==============================================
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384

# ==============================================
# ChromaDB Configuration
# ==============================================
CHROMA_COLLECTION_NAME = "veterinary_knowledge"

# ==============================================
# Chunking Configuration
# ==============================================
CHUNK_SIZE = 500          # tokens por chunk
CHUNK_OVERLAP = 50        # tokens de overlap entre chunks
SEPARATORS = ["\n\n", "\n", ". ", " "]

# ==============================================
# RAG Configuration
# ==============================================
RAG_TOP_K_RETRIEVAL = 10   # documentos a recuperar inicialmente
RAG_TOP_K_RERANK = 3       # documentos después del re-ranking
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ==============================================
# Prompts del sistema
# ==============================================
SYSTEM_PROMPT_RETRIEVER = """Eres un agente especializado en búsqueda de información veterinaria. 
Tu rol es analizar la pregunta del usuario, reformularla si es necesario para mejorar la búsqueda, 
y recuperar los documentos más relevantes de la base de conocimiento veterinario.

Debes ser preciso y exhaustivo en tu búsqueda. Si la pregunta es ambigua, 
busca información que cubra las posibles interpretaciones."""

SYSTEM_PROMPT_WRITER = """Eres un asistente veterinario profesional especializado en pequeños animales (perros y gatos).
Tu rol es redactar respuestas claras, precisas y profesionales basándote EXCLUSIVAMENTE en la información 
proporcionada por el agente buscador.

Reglas estrictas:
1. SOLO usa información de los documentos recuperados. NO inventes datos.
2. Cita las fuentes al final de cada afirmación relevante con el formato [Fuente: nombre_archivo].
3. Si la información es insuficiente, indícalo claramente.
4. Usa terminología veterinaria apropiada pero explica los términos técnicos.
5. Incluye siempre el disclaimer: "Esta información es de apoyo educativo y no sustituye el criterio de un médico veterinario."
6. Estructura tu respuesta con secciones claras cuando sea apropiado.
7. Responde siempre en español."""

# ==============================================
# Disclaimer
# ==============================================
DISCLAIMER = (
    "⚠️ **Aviso importante:** Este asistente es una herramienta de apoyo educativo "
    "y no sustituye el criterio profesional de un médico veterinario. "
    "Consulte siempre a un profesional para el diagnóstico y tratamiento de su mascota."
)
