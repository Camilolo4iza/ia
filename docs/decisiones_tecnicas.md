# 🧠 Decisiones de Diseño Técnico

Este documento recopila las decisiones de arquitectura más relevantes tomadas durante el desarrollo de **VetAssist AI**, detallando su contexto, la alternativa seleccionada y las consecuencias.

---

## Decisión 1: Groq API + Llama 3.3 70B como LLM Principal

### Contexto
El asistente clínico requiere un modelo de lenguaje con excelente comprensión lectora en español, capacidad para seguir instrucciones de formato complejas (como citación de fuentes en formato estricto y tags de control de estado), rapidez de respuesta (baja latencia) y que sea gratuito.

### Decisión
Utilizar la API de **Groq** con el modelo **`llama-3.3-70b-versatile`** en lugar de Google AI Studio (Gemini) u opciones locales completas (como Ollama Llama 3.2 3B).

### Justificación
1. **Velocidad de Inferencia**: Groq utiliza chips LPU (Language Processing Units) que procesan tokens a velocidades sumamente altas (habitualmente >250 tokens/s), reduciendo la latencia percibida en Streamlit drásticamente en comparación con APIs estándar.
2. **Capacidad de Razonamiento**: Llama 3.3 de 70 mil millones de parámetros tiene un desempeño comparable a GPT-4 en tareas de razonamiento RAG y estructuración, superando por amplio margen a modelos locales ligeros (ej. Llama 3.2 3B) que se ejecutarían lentos en la máquina local del usuario.

### Consecuencias
*   **Positivas**: Respuestas casi instantáneas, excelente seguimiento de prompts y soporte completo en español.
*   **Negativas**: Dependencia de conexión a internet activa y sujeción a los límites de tasa (rate limits) de la capa gratuita de Groq.

---

## Decisión 2: ChromaDB Local Persistente como Base de Datos Vectorial

### Contexto
Para el pipeline RAG, requerimos almacenar los fragmentos de texto del corpus junto con sus vectores de embeddings de forma persistente en el disco local, permitiendo consultas rápidas por similitud coseno e indexación eficiente.

### Decisión
Utilizar **ChromaDB** persistente local en lugar de FAISS o bases vectoriales en la nube (ej. Pinecone).

### Justificación
1. **Facilidad de Persistencia**: A diferencia de FAISS (que requiere guardar archivos pickle y recargar índices en memoria manualmente), ChromaDB provee un cliente persistente en disco nativo (`PersistentClient`) muy fácil de configurar.
2. **Metadatos Nativos**: Permite filtrar y guardar metadatos complejos (archivo de origen, sección, etc.) estructuradamente junto a los vectores sin requerir capas lógicas intermedias.
3. **Cero Dependencia de Cloud**: Al ser local, es 100% gratuita y los datos clínicos veterinarios no salen de la máquina local durante el indexado.

### Consecuencias
*   **Positivas**: Base de datos ligera, inicialización instantánea y código limpio sin dependencias de red.
*   **Negativas**: Los archivos ocupan espacio local en el disco y no es idóneo para escalar a millones de documentos (aunque es perfecto para nuestro corpus actual de 16 documentos).

---

## Decisión 3: Re-ranking de Dos Etapas con Cross-Encoder

### Contexto
La búsqueda semántica convencional a veces recupera fragmentos que comparten palabras clave similares pero que no responden en absoluto a la pregunta del veterinario, lo que introduce ruido en la ventana de contexto del LLM y eleva la probabilidad de alucinaciones.

### Decisión
Implementar un pipeline de recuperación en dos etapas: Búsqueda Vectorial Rápida (Top-10) -> Re-ranking Semántico con **`cross-encoder/ms-marco-MiniLM-L-6-v2`** (Top-3).

### Justificación
1. **Precisión Semántica**: Un Cross-Encoder analiza la pregunta y el fragmento simultáneamente en el modelo transformer (self-attention mutuo), determinando con precisión milimétrica si el texto responde a la pregunta. Los modelos Bi-Encoder (vectores independientes) no tienen esta capacidad cruzada.
2. **Eficiencia**: Ejecutar un Cross-Encoder en toda la base de datos es extremadamente lento. Al restringir el re-ranking únicamente a los top-10 resultados previamente filtrados por similitud vectorial, obtenemos los beneficios de alta precisión con una latencia mínima de procesamiento (~150ms).

### Consecuencias
*   **Positivas**: Descarte casi absoluto de falsos positivos en el contexto provisto al LLM. Reducción sustancial del consumo de tokens al inyectar solo 3 fragmentos hiper-relevantes en lugar de 10.
*   **Negativas**: Mayor consumo de memoria RAM local en la inicialización al cargar un segundo modelo de transformer (`cross-encoder`).
