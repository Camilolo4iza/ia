# 🏛️ Arquitectura General — VetAssist AI

Este documento describe la estructura y el flujo de datos global de **VetAssist AI**, un asistente veterinario especializado para clínicas de pequeños animales.

## Diagrama de Arquitectura

El sistema está diseñado bajo una arquitectura desacoplada y modular que combina interfaces de usuario en tiempo real, orquestación de agentes con grafos de estado, bases de datos vectoriales locales e integración de herramientas a través del Model Context Protocol (MCP).

```mermaid
graph TD
    %% Capa de Presentación
    subgraph UI [Capa de Presentación]
        App[Streamlit Web App]
    end

    %% Capa de Orquestación y Agentes
    subgraph Agents [Orquestación de Agentes]
        Graph[LangGraph StateGraph]
        RetrieverAgent[Retriever Agent - Buscador]
        WriterAgent[Writer Agent - Redactor]
    end

    %% Capa de Negocio e Inteligencia
    subgraph RAG [Capa RAG]
        Pipeline[RAG Pipeline Controller]
        Loader[Document Loader]
        Chunker[Section Chunker]
        Embedder[SentenceTransformer Embedder]
        Reranker[CrossEncoder Reranker]
    end

    %% Capa de Almacenamiento
    subgraph Storage [Capa de Persistencia]
        VectorStore[ChromaDB Local Vector Store]
        Corpus[(Corpus Veterinario: 16 txt)]
    end

    %% Capa de Servicios Externos
    subgraph External [Servicios de IA]
        Groq[Groq API: Llama 3.3 70B]
    end

    %% Capa de Herramientas y Skills
    subgraph Tools [Herramientas & Skills]
        MCP[FastMCP Server]
        PDF[PDF Report Generator Skill]
    end

    %% Flujos y Conexiones
    App -->|1. Pregunta & Datos Paciente| Graph
    Graph -->|Orquesta| RetrieverAgent
    Graph -->|Orquesta| WriterAgent
    
    RetrieverAgent -->|2. Reformula & Busca| Pipeline
    Pipeline -->|Lee| VectorStore
    VectorStore -->|Recupera Top-10| Reranker
    Reranker -->|Re-ordena Top-3| Pipeline
    
    Pipeline -->|Devuelve Contexto| RetrieverAgent
    RetrieverAgent -->|Acumula Contexto| Graph
    
    WriterAgent -->|3. Valida & Consulta LLM| Groq
    Groq -->|Genera Respuesta| WriterAgent
    
    WriterAgent -->|4. Si falta info, repite| RetrieverAgent
    WriterAgent -->|5. Respuesta Final| Graph
    
    %% Herramientas
    App -->|Consulta widget| MCP
    App -->|Exporta reporte| PDF
    
    %% Inicialización
    Loader -->|Lee raw files| Corpus
    Chunker -->|Fragmenta por sección| Loader
    Embedder -->|Genera embeddings| Chunker
    Embedder -->|Guarda| VectorStore
    
    %% Estilo de componentes
    style App fill:#2980b9,stroke:#1a5276,stroke-width:2px,color:#fff
    style Graph fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#fff
    style Pipeline fill:#8e44ad,stroke:#6c3483,stroke-width:2px,color:#fff
    style VectorStore fill:#f39c12,stroke:#d35400,stroke-width:2px,color:#fff
    style Groq fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
    style MCP fill:#16a085,stroke:#117a65,stroke-width:2px,color:#fff
    style PDF fill:#138d75,stroke:#117a65,stroke-width:2px,color:#fff
```

## Componentes Principales

1. **Interfaz Streamlit (`src/app.py`)**: Interfaz gráfica del usuario (GUI) que expone el chat con el asistente, la ficha de registro del paciente (perro/gato, peso, edad), widgets para herramientas clínicas rápidas (dosis y vacunas) y el disparador para exportación a PDF.
2. **Orquestador LangGraph (`src/agents/graph.py`)**: Coordina el ciclo de vida de los agentes mediante un grafo con estados persistentes. Si el agente redactor determina que no hay suficiente información, reenvía el flujo de vuelta al buscador con retroalimentación.
3. **Agente Buscador (`src/agents/retriever_agent.py`)**: Reformula y optimiza la pregunta del usuario utilizando el LLM, realiza la búsqueda y acumula los documentos.
4. **Agente Redactor (`src/agents/writer_agent.py`)**: Valida la relevancia y suficiencia del contexto recuperado. Si es apto, redacta la respuesta, le da el tono clínico apropiado, cita las fuentes de manera estructurada e inserta el disclaimer legal.
5. **Controlador RAG (`src/retrieval/rag_pipeline.py`)**: Expone la lógica de ingesta y recuperación. Integra el cargador, fragmentador semántico, modelo local de embeddings y el re-ranker.
6. **Re-ranker Cross-Encoder (`src/retrieval/reranker.py`)**: Implementa un re-ranking secundario utilizando un modelo pesado entrenado para puntuar la relevancia de pares (pregunta, fragmento) de forma cruzada, reduciendo falsos positivos del espacio vectorial tradicional.
7. **Servidor MCP (`src/mcp/vet_mcp_server.py`)**: Implementa el protocolo estándar Model Context Protocol usando FastMCP. Provee cálculos matemáticos precisos de dosificación y esquemas de vacunación.
8. **Skill Reporte PDF (`src/skills/report_skill.py`)**: Genera de forma asíncrona un archivo PDF con la ficha completa del paciente, anamnesis/conversación e indicaciones sugeridas.
