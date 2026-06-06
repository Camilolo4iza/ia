import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

from src.agents.graph import VeterinaryAgentGraph
from src.config import DISCLAIMER, GROQ_API_KEY
from src.mcp.vet_mcp_server import calcular_dosis, consultar_vacunas
from src.retrieval.rag_pipeline import VeterinaryRAGPipeline
from src.skills.report_skill import ClinicalReportGenerator


st.set_page_config(
    page_title="VetAssist AI - Clínica",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(22, 163, 74, 0.12), transparent 40rem),
            linear-gradient(135deg, #07130f 0%, #0b1613 48%, #101418 100%);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b2218 0%, #11261e 100%);
        border-right: 1px solid rgba(134, 239, 172, 0.15);
    }

    section[data-testid="stSidebar"] img {
        background: #dcfce7;
        padding: 12px;
        border-radius: 999px;
        border: 1px solid rgba(22, 163, 74, 0.4);
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    section[data-testid="stSidebar"] img:hover {
        transform: rotate(8deg) scale(1.08);
        box-shadow: 0 0 20px rgba(74, 222, 128, 0.4);
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .clinical-header {
        background:
            linear-gradient(135deg, rgba(13, 148, 136, 0.85), rgba(22, 163, 74, 0.85)),
            url("https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-position: center 30%;
        padding: 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: transform 0.3s ease;
    }

    .clinical-header:hover {
        transform: translateY(-3px);
    }

    .clinical-header h1 {
        margin: 0;
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }

    .clinical-header p {
        margin: 12px 0 0 0;
        opacity: 0.95;
        font-size: 1.15rem;
        max-width: 800px;
        line-height: 1.5;
        text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }

    .header-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }

    .header-badge {
        background: rgba(4, 47, 46, 0.5);
        border: 1px solid rgba(134, 239, 172, 0.4);
        border-radius: 999px;
        padding: 8px 16px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #ecfdf5;
        backdrop-filter: blur(8px);
        animation: float 4s ease-in-out infinite;
    }

    .header-badge:nth-child(2) { animation-delay: 1s; }
    .header-badge:nth-child(3) { animation-delay: 2s; }
    .header-badge:nth-child(4) { animation-delay: 3s; }

    .disclaimer-banner {
        background: linear-gradient(90deg, rgba(236, 253, 245, 0.95), rgba(209, 250, 229, 0.95));
        border-left: 6px solid #16a34a;
        padding: 16px 20px;
        border-radius: 12px;
        color: #064e3b;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 20px;
        margin: 15px 0 25px 0;
    }

    .status-card, .example-card, .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(134, 239, 172, 0.15);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        backdrop-filter: blur(12px);
    }

    .status-card:hover, .example-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 22px 45px rgba(22, 163, 74, 0.2);
        border-color: #4ade80;
        background: rgba(15, 23, 42, 0.8);
    }

    .metric-card {
        border-left: 6px solid #22c55e;
        color: #f8fafc;
        margin-bottom: 16px;
    }

    .status-card strong, .example-card strong, .metric-card strong {
        color: #86efac;
        display: block;
        margin-bottom: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .status-card span, .example-card span, .metric-card span {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    code {
        color: #86efac !important;
        background: rgba(20, 83, 45, 0.5) !important;
        border-radius: 6px;
        padding: 3px 6px;
        font-weight: 600;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 1.1rem;
        transition: color 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        color: #4ade80 !important;
        border-bottom-color: #4ade80 !important;
    }

    .stButton button, .stDownloadButton button, div[data-testid="stFormSubmitButton"] button {
        border-radius: 12px;
        border: 1px solid rgba(134, 239, 172, 0.4);
        background: linear-gradient(135deg, #16a34a, #0d9488);
        color: white;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(22, 163, 74, 0.3);
    }

    .stButton button:hover, .stDownloadButton button:hover, div[data-testid="stFormSubmitButton"] button:hover {
        border-color: #86efac;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(22, 163, 74, 0.45);
        filter: brightness(1.15);
    }

    /* Chat Styling */
    .stChatMessage {
        background-color: rgba(15, 23, 42, 0.4);
        border-radius: 12px;
        padding: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 15px;
    }
    
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(20, 83, 45, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.15);
    }

    @media (max-width: 900px) {
        .dashboard-grid { grid-template-columns: 1fr; }
        .clinical-header { padding: 25px; }
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# --- INICIALIZACIÓN DE ESTADOS ---
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = VeterinaryRAGPipeline()
    try:
        st.session_state.rag_pipeline.ingest(force=False)
    except Exception as exc:
        print(f"Error en ingesta inicial: {exc}")

if "agent_graph" not in st.session_state:
    st.session_state.agent_graph = VeterinaryAgentGraph(st.session_state.rag_pipeline)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "paciente_guardado" not in st.session_state:
    st.session_state.paciente_guardado = False

try:
    corpus_stats = st.session_state.rag_pipeline.vector_store.get_stats()
except Exception:
    corpus_stats = {"collection_name": "veterinary_knowledge", "total_chunks": "N/D"}

# --- HEADER INTERACTIVO ---
st.markdown(
    """
<div class="clinical-header">
    <h1>VetAssist AI ⚕️</h1>
    <p>Asistente clínico veterinario interactivo con RAG, agentes autónomos, calculadoras MCP y generación de reportes automáticos.</p>
    <div class="header-badges">
        <span class="header-badge">🔍 RAG Dinámico</span>
        <span class="header-badge">🤖 Agentes LangGraph</span>
        <span class="header-badge">🧮 FastMCP Tools</span>
        <span class="header-badge">📄 Exportación PDF</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

clean_disclaimer = DISCLAIMER.replace("**", "").replace("⚠️", "⚕️ AVISO CLÍNICO:")
st.markdown(f'<div class="disclaimer-banner"><strong>{clean_disclaimer}</strong></div>', unsafe_allow_html=True)

# --- SIDEBAR INTERACTIVO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/194/194279.png", width=90)
    st.markdown("### 📋 Expediente del Paciente")

    with st.form("paciente_form"):
        p_nombre = st.text_input("Nombre de la mascota", value="Toby")
        p_especie = st.selectbox("Especie", options=["Perro", "Gato"])
        p_raza = st.text_input("Raza", value="Golden Retriever" if p_especie == "Perro" else "Siamés")
        
        col1, col2 = st.columns(2)
        with col1:
            p_edad = st.text_input("Edad", value="3 años")
        with col2:
            p_peso = st.number_input(
                "Peso (kg)",
                min_value=0.1,
                max_value=120.0,
                value=25.0 if p_especie == "Perro" else 4.2,
            )
        
        submit_paciente = st.form_submit_button("💾 Guardar y Actualizar")

    paciente_info = {
        "nombre": p_nombre,
        "especie": p_especie,
        "raza": p_raza,
        "edad": p_edad,
        "peso": p_peso,
    }

    if submit_paciente:
        st.session_state.paciente_guardado = True
        st.toast(f"Ficha clínica de {p_nombre} guardada exitosamente", icon="✅")

    if st.session_state.paciente_guardado:
        st.success(f"**Paciente Activo:** {p_nombre} ({p_especie}, {p_peso} kg)")

    st.markdown("---")
    st.markdown("### 🧰 Herramientas MCP Rápidas")

    tab_dosis, tab_vacunas = st.tabs(["💊 Dosis", "💉 Vacunas"])

    with tab_dosis:
        calc_med = st.selectbox(
            "Principio activo",
            ["Meloxicam", "Amoxicilina", "Cefalexina", "Metronidazol"],
        )
        if st.button("Calcular dosis", use_container_width=True):
            with st.spinner("Calculando..."):
                res_dosis = calcular_dosis(calc_med, paciente_info["peso"], paciente_info["especie"])
                st.info(res_dosis)
                st.toast("Dosis calculada", icon="💊")

    with tab_vacunas:
        edad_semanas = st.slider("Edad en semanas", min_value=1, max_value=104, value=8)
        paciente_info["edad_semanas"] = edad_semanas
        if st.button("Consultar esquema", use_container_width=True):
            with st.spinner("Buscando..."):
                res_vacunas = consultar_vacunas(paciente_info["especie"], edad_semanas)
                st.success(res_vacunas)
                st.toast("Esquema recuperado", icon="💉")

# --- AREA PRINCIPAL CON TABS ---
tab_chat, tab_dashboard = st.tabs(["💬 Panel de Asistencia Virtual", "📊 Estado del Sistema RAG"])

with tab_dashboard:
    st.markdown("### Métricas y Estado del Corpus")
    st.markdown(
        f"""
    <div class="dashboard-grid">
        <div class="status-card">
            <strong>📚 Corpus Veterinario Activo</strong>
            <span>16 documentos especializados indexados. Incluye protocolos de urgencias, nutrición clínica, cirugía y farmacología.</span>
        </div>
        <div class="status-card">
            <strong>🧠 Motor de Búsqueda (ChromaDB)</strong>
            <span>Colección <code>{corpus_stats["collection_name"]}</code> operando localmente con <code>{corpus_stats["total_chunks"]}</code> fragmentos semánticos (chunks).</span>
        </div>
        <div class="status-card">
            <strong>⚙️ Modelo LLM Principal</strong>
            <span>Conectado a <code>Groq</code> (Llama-3.3-70b). Los agentes Retriever y Writer están listos para orquestar respuestas.</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Re-indexar Documentos (Forzar Ingesta)"):
        with st.spinner("Vectorizando y creando chunks semánticos..."):
            res_ingest = st.session_state.rag_pipeline.ingest(force=True)
            st.success(res_ingest["message"])
            st.toast("Base de datos vectorial actualizada", icon="🔄")
            st.rerun()

with tab_chat:
    if not GROQ_API_KEY:
        st.error("⚠️ Clave API de Groq no detectada: configura `GROQ_API_KEY` en el archivo `.env`.")

    if not st.session_state.chat_history:
        st.markdown(
            """
        <div class="dashboard-grid">
            <div class="example-card">
                <strong>🛡️ Ejemplo: Prevención</strong>
                <span>"¿Qué vacunas necesita un cachorro de 8 semanas y cuándo debe volver?"</span>
            </div>
            <div class="example-card">
                <strong>🚨 Ejemplo: Urgencias</strong>
                <span>"¿Qué signos indican torsión gástrica y cuál es el manejo inicial?"</span>
            </div>
            <div class="example-card">
                <strong>⚕️ Ejemplo: Farmacología</strong>
                <span>"Calcula la dosis de meloxicam para un perro de 25 kg y explica precauciones."</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Mostrar historial de chat con avatares dinámicos
    for message in st.session_state.chat_history:
        avatar = "👤" if message["role"] == "user" else "🐾"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            
            # Mostrar herramientas y fuentes en columnas para mejor diseño
            if message.get("tool_outputs") or message.get("sources"):
                col_t, col_s = st.columns(2)
                with col_t:
                    if message.get("tool_outputs"):
                        with st.expander("🛠️ MCP Tools Ejecutadas"):
                            for output in message["tool_outputs"]:
                                st.info(output)
                with col_s:
                    if message.get("sources"):
                        with st.expander("📚 Fuentes RAG Consultadas"):
                            for src in message["sources"]:
                                st.caption(f"- {src}")

    # Input del chat
    if prompt := st.chat_input(f"Consultar para {p_nombre} sobre síntomas, tratamientos o diagnósticos..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🐾"):
            with st.spinner("🕵️‍♂️ Consultando la base de datos veterinaria y orquestando respuesta..."):
                response_dict = st.session_state.agent_graph.ask(prompt, patient_info=paciente_info)
                answer = response_dict["answer"]
                sources = response_dict.get("sources", [])
                tool_outputs = response_dict.get("tool_outputs", [])

                st.markdown(answer)

                if tool_outputs or sources:
                    col_t, col_s = st.columns(2)
                    with col_t:
                        if tool_outputs:
                            with st.expander("🛠️ MCP Tools Ejecutadas"):
                                for output in tool_outputs:
                                    st.info(output)
                    with col_s:
                        if sources:
                            with st.expander("📚 Fuentes RAG Consultadas"):
                                for src in sources:
                                    st.caption(f"- {src}")

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "tool_outputs": tool_outputs,
                    }
                )

    # Generación de Reporte al final
    if len(st.session_state.chat_history) > 1:
        st.markdown("---")
        col_text, col_btn = st.columns([2, 1])
        
        with col_text:
            st.markdown("#### 📄 Exportación Clínica")
            st.write(f"Genera un reporte formal en PDF combinando los datos de **{p_nombre}** y la consulta actual.")
            
        with col_btn:
            if st.button("Generar Reporte PDF", use_container_width=True):
                conversacion_acumulada = ""
                for msg in st.session_state.chat_history:
                    role_label = "Mascota/Tutor" if msg["role"] == "user" else "Veterinario Asistente"
                    conversacion_acumulada += f"[{role_label}]: {msg['content']}\n\n"

                ultimas_recomendaciones = "Ver conversación adjunta en el cuerpo de la consulta."
                for msg in reversed(st.session_state.chat_history):
                    if msg["role"] == "assistant":
                        ultimas_recomendaciones = msg["content"]
                        break

                # Recolectar todas las fuentes y herramientas de la sesión
                todas_las_fuentes = []
                todas_las_herramientas = []
                
                for msg in st.session_state.chat_history:
                    if "sources" in msg and msg["sources"]:
                        todas_las_fuentes.extend(msg["sources"])
                    if "tool_outputs" in msg and msg["tool_outputs"]:
                        todas_las_herramientas.extend(msg["tool_outputs"])

                with st.spinner("Compilando documento PDF..."):
                    # Instanciar fresco para evitar problemas de caché de session_state
                    report_generator = ClinicalReportGenerator()
                    pdf_path = report_generator.generate(
                        paciente=paciente_info,
                        consulta_texto=conversacion_acumulada[:1500]
                        + "\n[Resumen truncado para legibilidad del reporte...]",
                        recomendaciones=ultimas_recomendaciones[:1500],
                        herramientas=todas_las_herramientas,
                        fuentes=todas_las_fuentes
                    )

                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()

                    st.balloons()
                    st.toast("Reporte clínico generado exitosamente", icon="🎉")
                    
                    st.download_button(
                        label="⬇️ Descargar Archivo PDF",
                        data=pdf_bytes,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        use_container_width=True
                    )
