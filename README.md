# 🐾 VetAssist AI — Asistente Clínico Inteligente

VetAssist AI es un asistente inteligente diseñado para clínicas y centros de salud animal. El sistema permite al personal médico veterinario realizar consultas en lenguaje natural sobre diagnósticos, tratamientos, vacunas, dosificaciones y protocolos clínicos, devolviendo respuestas fundamentadas en un corpus de conocimiento local, citando fuentes formales y generando reportes clínicos en PDF.

El proyecto integra arquitecturas avanzadas de Procesamiento de Lenguaje Natural (NLP):
1. **Pipeline RAG (Retrieval-Augmented Generation)**: Con búsqueda vectorial en base local y una etapa secundaria de **Re-ranking semántico con Cross-Encoder** para garantizar relevancia de contexto.
2. **Orquestación Multi-Agente con LangGraph**: Flujo coordinado entre un Agente Buscador (Retriever) y un Agente Redactor (Writer) con bucle de validación/retroalimentación.
3. **Servidor MCP (Model Context Protocol)**: Exposición estándar de herramientas clínicas complejas (cálculo de dosificación y consultas de calendarios de vacunación).
4. **Skills Especializadas**: Generación automatizada de reportes clínicos en formato PDF.

---

## 📂 Estructura del Proyecto

```
ProyectoFinalIA/
├── src/
│   ├── __init__.py
│   ├── app.py                    # Interfaz de usuario Streamlit principal
│   ├── config.py                 # Constantes y configuración centralizada
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py             # Carga recursiva de archivos raw
│   │   ├── chunker.py            # Fragmentador semántico por secciones
│   │   └── embedder.py           # Generador de embeddings (sentence-transformers)
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_store.py       # Controlador de ChromaDB
│   │   ├── reranker.py           # Re-ranking con Cross-Encoder (MiniLM)
│   │   └── rag_pipeline.py       # Pipeline RAG unificado
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py              # Estado compartido de agentes
│   │   ├── retriever_agent.py    # Agente Buscador
│   │   ├── writer_agent.py       # Agente Redactor (Guardrail)
│   │   └── graph.py              # Compilador del grafo de LangGraph
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── vet_mcp_server.py     # Servidor MCP (FastMCP) con herramientas clínicas
│   └── skills/
│       ├── __init__.py
│       └── report_skill.py       # Habilidad: exportar informe médico PDF
├── docs/
│   ├── arquitectura_general.md   # Arquitectura y diagrama Mermaid
│   ├── flujo_rag.md              # Detalle de ingesta y búsqueda vectorial
│   ├── interaccion_agentes.md    # Detalle de LangGraph y secuencia
│   └── decisiones_tecnicas.md    # Justificaciones tecnológicas y trade-offs
├── data/
│   ├── raw/                      # 16 documentos veterinarios del corpus (.txt)
│   └── processed/                # Directorio de persistencia de ChromaDB
├── tests/
│   ├── __init__.py
│   ├── test_chunker.py           # Pruebas del chunker
│   ├── test_rag_pipeline.py      # Pruebas del pipeline RAG
│   └── test_agents.py            # Pruebas del flujo multiagente
├── requirements.txt              # Dependencias del proyecto
├── .env.example                  # Ejemplo de variables de entorno
├── .gitignore                    # Reglas de exclusión de git
└── README.md                     # Guía principal (este archivo)
```

---

## 🛠️ Instalación y Configuración

### Requisitos Previos
* **Python 3.10 o superior** (Se recomienda Python 3.12).
* **Conexión a Internet** (para llamadas al LLM de Groq y descargas iniciales de modelos).

### Paso 1: Configurar el Entorno Virtual
Abre una terminal en la raíz del proyecto y crea un entorno virtual:
```bash
# Crear entorno
py -m venv .venv

# Activar en Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Activar en Windows (CMD)
.venv\Scripts\activate.bat
```

### Paso 2: Instalar Dependencias
Instala los paquetes necesarios indicados en `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Clave API
1. Registra una cuenta gratuita en [console.groq.com](https://console.groq.com) y genera una API key.
2. Duplica el archivo `.env.example` y renómbralo a `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edita `.env` e inserta tu clave:
   ```env
   GROQ_API_KEY=gsk_tu_clave_real_de_groq_aqui
   ```

---

## 🚀 Uso del Sistema

### 1. Ejecutar la Aplicación Web (Streamlit)
Para lanzar la interfaz gráfica en tu navegador local, ejecuta:
```bash
streamlit run src/app.py
```
*La interfaz se abrirá automáticamente en `http://localhost:8501`.*

**Uso de la Interfaz:**
1. **Ficha del Paciente (Sidebar)**: Registra el nombre, especie, edad y peso de la mascota. Estos datos se usarán para cálculos dosificadores automáticos y para la cabecera del informe.
2. **Calculadora Rápida (Sidebar)**: Permite ingresar un fármaco y calcular la dosis al instante (MCP) o consultar el esquema de vacunas.
3. **Chat de Consulta (Main)**: Haz preguntas al asistente. Verás la respuesta formulada, las fuentes consultadas y podrás descargar un reporte formal en PDF haciendo clic en "Generar Reporte PDF".

### 2. Ejecutar y Probar el Servidor MCP
El servidor Model Context Protocol de VetAssist AI se encuentra en `src/mcp/vet_mcp_server.py`. Puedes levantarlo o probar sus herramientas utilizando el Inspector de MCP oficial:
```bash
npx -y @modelcontextprotocol/inspector python src/mcp/vet_mcp_server.py
```

---

## 🧪 Pruebas Unitarias

El proyecto cuenta con un set de pruebas automatizadas con `pytest`. Para ejecutarlas y validar la consistencia del código, corre:
```bash
pytest tests/ -v
```

---

## 👥 Autores y Créditos
* **Integrante 1**: [Nombre Completo - Correo]
* **Integrante 2**: [Nombre Completo - Correo]

*Materia: Inteligencia Artificial / Proyecto Final de Semestre.*
