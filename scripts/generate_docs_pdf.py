import os
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_PDF = PROJECT_ROOT / "docs" / "documentacion_tecnica.pdf"

def sanitize_text(text: str) -> str:
    """Sanitiza texto para evitar crasheos de encoding en FPDF (latin-1)."""
    if not isinstance(text, str):
        return ""
    text = text.replace("—", "-").replace("–", "-").replace("”", '"').replace("“", '"')
    text = text.replace("🐾", "").replace("👤", "").replace("⚕️", "").replace("✅", "").replace("🚨", "")
    text = text.replace("🌟", "").replace("🏗️", "").replace("📂", "").replace("🛠️", "").replace("🚀", "")
    text = text.replace("🧪", "").replace("🧠", "").replace("🏛️", "").replace("📋", "").replace("💡", "")
    text = text.replace("⚠️", "").replace("💉", "").replace("💊", "").replace("📊", "").replace("🔄", "")
    return text.encode('latin-1', 'replace').decode('latin-1')

class TechDocPDF(FPDF):
    """PDF personalizado para la documentación de VetAssist AI."""
    def header(self):
        # Fondo del encabezado
        self.set_fill_color(40, 116, 166)  # Azul clínico premium
        self.rect(0, 0, 210, 15, 'F')
        
        # Texto del encabezado
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, -5, sanitize_text("VETASSIST AI - DOCUMENTACIÓN TÉCNICA OFICIAL"), 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        # Texto del pie
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, sanitize_text("Soporte Técnico de Inteligencia Artificial - Proyecto Final"), 0, 0, 'L')
        self.cell(0, 5, sanitize_text(f"Página {self.page_no()}/{{nb}}"), 0, 1, 'R')

def build_pdf():
    pdf = TechDocPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # ----------------------------------------------------
    # Portada / Título Principal
    # ----------------------------------------------------
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, sanitize_text("VetAssist AI"), 0, 1, 'L')
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 8, sanitize_text("Copiloto Clínico e Inteligencia Artificial para Veterinaria"), 0, 1, 'L')
    
    # Metadatos del Documento
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(127, 140, 141)
    fecha_str = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 5, sanitize_text(f"Fecha de Generación: {fecha_str}  |  Entorno: Producción"), 0, 1, 'L')
    pdf.ln(10)
    
    # ----------------------------------------------------
    # SECCIÓN 1: DESCRIPCIÓN DEL DOMINIO Y CASOS DE USO
    # ----------------------------------------------------
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 166)
    pdf.cell(0, 8, sanitize_text("1. DESCRIPCIÓN DEL DOMINIO Y CASOS DE USO"), 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(44, 62, 80)
    
    intro_text = (
        "VetAssist AI es un sistema inteligente diseñado para asistir a profesionales de la medicina veterinaria "
        "(en particular canina y felina) en la toma de decisiones clínicas diarias, consulta rápida de manuales, "
        "esquemas de vacunación y dosificaciones de fármacos.\n\n"
        "Casos de Uso Principales:\n"
        "  - Soporte Clínico en Tiempo Real: Consultas diagnósticas complejas resueltas en segundos basándose en manuales.\n"
        "  - Calculadora de Dosis Determinista: Cálculo exacto de mililitros o miligramos según el peso corporal.\n"
        "  - Tablas de Inmunización: Consulta interactiva y estructurada de calendarios preventivos por edad.\n"
        "  - Reportes Clínicos en PDF: Exportación formal de la consulta y sus fuentes citadas."
    )
    pdf.multi_cell(0, 5, sanitize_text(intro_text))
    pdf.ln(8)
    
    # ----------------------------------------------------
    # SECCIÓN 2: ARQUITECTURA GENERAL
    # ----------------------------------------------------
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 166)
    pdf.cell(0, 8, sanitize_text("2. ARQUITECTURA GENERAL DEL SISTEMA"), 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(44, 62, 80)
    
    arq_text = (
        "El sistema implementa una arquitectura modular de cuatro capas:\n"
        "  1. Capa de Presentación: Desarrollada en Streamlit (src/app.py) para proporcionar una GUI fluida y moderna.\n"
        "  2. Capa de Orquestación: Gestionada por LangGraph mediante un grafo de estados (StateGraph) que coordina los agentes.\n"
        "  3. Capa RAG (Generación Aumentada por Recuperación): Une la segmentación de texto, embeddings locales y re-ranking.\n"
        "  4. Capa de Persistencia: Una base de datos vectorial local basada en ChromaDB.\n\n"
        "Los agentes implementados son:\n"
        "  - Retriever Agent: Su objetivo es optimizar y reformular la query para buscar el mejor contexto bibliográfico.\n"
        "  - Writer Agent: Su objetivo es redactar la respuesta clínica, verificar la suficiencia de la información y citar fuentes."
    )
    pdf.multi_cell(0, 5, sanitize_text(arq_text))
    pdf.ln(8)
    
    # ----------------------------------------------------
    # SECCIÓN 3: PIPELINE RAG Y EMBEDDINGS
    # ----------------------------------------------------
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 166)
    pdf.cell(0, 8, sanitize_text("3. PIPELINE RAG Y BASE VECTORIAL LOCAL"), 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(44, 62, 80)
    
    rag_text = (
        "Para garantizar precisión clínica y mitigar alucinaciones de la IA, implementamos un pipeline RAG local:\n"
        "  - Chunking Semántico por Secciones: Diseñamos un fragmentador adaptativo (SectionChunker) que corta los documentos "
        "respetando títulos y subtítulos (tomas lógicas) con un límite de 500 palabras y solape de 50 palabras.\n"
        "  - Generación de Embeddings: Usamos el modelo local 'paraphrase-multilingual-MiniLM-L12-v2' que mapea los textos a "
        "coordenadas de 384 dimensiones. Al ser local, es 100% privado y gratuito.\n"
        "  - Motor de Búsqueda Vectorial: ChromaDB actúa como almacenamiento indexado en disco local. Se realiza una "
        "recuperación inicial por similitud coseno seleccionando los 10 fragmentos candidatos (Top-K=10)."
    )
    pdf.multi_cell(0, 5, sanitize_text(rag_text))
    pdf.ln(8)
    
    # Forzar cambio de página para las siguientes secciones importantes
    pdf.add_page()
    
    # ----------------------------------------------------
    # SECCIÓN 4: RE-RANKING CON CROSS-ENCODER
    # ----------------------------------------------------
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 166)
    pdf.cell(0, 8, sanitize_text("4. RE-RANKING DE DOS ETAPAS (CROSS-ENCODER)"), 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(44, 62, 80)
    
    rerank_text = (
        "Los sistemas de recuperación tradicionales basados únicamente en embeddings a veces recuperan fragmentos que "
        "tienen similitud de vocabulario pero que no responden en absoluto a la intención de la pregunta clínica.\n\n"
        "Para solucionar esto, añadimos una segunda etapa de filtrado mediante un modelo Cross-Encoder "
        "('cross-encoder/ms-marco-MiniLM-L-6-v2'). A diferencia del Bi-Encoder (que procesa la pregunta y el texto por "
        "separado), el Cross-Encoder evalúa la consulta del veterinario y cada fragmento simultáneamente en su red de "
        "atención. Esto calcula una puntuación de coincidencia exacta y reordena los 10 fragmentos iniciales. "
        "Solo los 3 mejores fragmentos con el mayor puntaje de Cross-Encoder se envían a la ventana de contexto del LLM. "
        "Esto descarta casi al 100% el contexto ruidoso o irrelevante."
    )
    pdf.multi_cell(0, 5, sanitize_text(rerank_text))
    pdf.ln(8)
    
    # ----------------------------------------------------
    # SECCIÓN 5: INTEGRACIÓN DE HERRAMIENTAS VÍA MCP
    # ----------------------------------------------------
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 166)
    pdf.cell(0, 8, sanitize_text("5. INTEGRACIÓN DE HERRAMIENTAS CLÍNICAS (MCP)"), 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(44, 62, 80)
    
    mcp_text = (
        "Los LLMs nativamente fallan con frecuencia en operaciones matemáticas básicas. En un entorno de salud, un error "
        "en una dosificación puede ser crítico.\n\n"
        "Para asegurar total fiabilidad, implementamos un servidor bajo el estándar abierto Model Context Protocol "
        "(MCP) utilizando FastMCP en Python. Esto expone funciones de cálculo deterministas externas que el LLM puede "
        "invocar de forma autónoma:\n"
        "  - calcular_dosis: Calcula miligramos y mililitros basados en el principio activo, concentración y peso del paciente.\n"
        "  - consultar_vacunas: Devuelve las tablas oficiales de vacunación en base a la edad de la mascota.\n\n"
        "Al delegar estas operaciones a funciones Python tradicionales, combinamos la fluidez conversacional del LLM "
        "con la precisión e infalibilidad de la programación estructurada."
    )
    pdf.multi_cell(0, 5, sanitize_text(mcp_text))
    pdf.ln(8)
    
    # ----------------------------------------------------
    # SECCIÓN 6: DECISIONES TÉCNICAS Y JUSTIFICACIONES
    # ----------------------------------------------------
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 166)
    pdf.cell(0, 8, sanitize_text("6. DECISIONES CLAVE DE DISEÑO Y TRADE-OFFS"), 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(44, 62, 80)
    
    decisiones_text = (
        "1. Groq + Llama 3.3 70B: Proporciona razonamiento lógico de alto nivel y excelente soporte en español con "
        "latencias de inferencia sumamente bajas (gracias a los procesadores LPU de Groq).\n"
        "2. ChromaDB Persistente: Nos permite indexar, guardar y leer vectores de embeddings en disco local sin costos "
        "adicionales, con soporte nativo de metadatos y filtrado ágil.\n"
        "3. Validación en LangGraph (Loop de Agentes): Si la información disponible en la base de datos es insuficiente "
        "para responder de forma segura, el Writer Agent detiene la generación, activa la bandera 'missing_info' y regresa "
        "al Retriever para una segunda búsqueda dirigida, evitando responder con mentiras o adivinaciones."
    )
    pdf.multi_cell(0, 5, sanitize_text(decisiones_text))
    pdf.ln(15)
    
    # firmas
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(95, 5, sanitize_text("Firma del Desarrollador Principal"), 0, 0, 'C')
    pdf.cell(95, 5, sanitize_text("Firma del Evaluador Académico"), 0, 1, 'C')
    
    pdf.ln(10)
    pdf.cell(95, 5, "_______________________", 0, 0, 'C')
    pdf.cell(95, 5, "_______________________", 0, 1, 'C')
    
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(95, 5, "Ingeniería de Software / IA", 0, 0, 'C')
    pdf.cell(95, 5, sanitize_text("Sustentación de Proyecto Final"), 0, 1, 'C')

    # Guardar PDF
    pdf.output(str(OUTPUT_PDF))
    print(f"PDF generado con éxito en: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
