import os
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
from src.config import REPORTS_DIR, DISCLAIMER
import unicodedata

def sanitize_text(text: str) -> str:
    """Elimina caracteres unicode no soportados por las fuentes estándar de FPDF (latin-1)."""
    if not isinstance(text, str):
        return ""
    # Reemplazos específicos comunes
    text = text.replace("—", "-").replace("–", "-").replace("”", '"').replace("“", '"')
    text = text.replace("🐾", "").replace("👤", "").replace("⚕️", "").replace("✅", "").replace("🚨", "")
    # Normalizar a ASCII y luego a string de nuevo, o forzar latin-1
    return text.encode('latin-1', 'replace').decode('latin-1')

class VeterinaryReportPDF(FPDF):
    """
    Clase PDF personalizada para dar un estilo premium y estructurado al reporte clínico.
    """
    def header(self):
        self.set_fill_color(40, 116, 166)  # Azul clínico premium
        self.rect(0, 0, 210, 15, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, -5, sanitize_text('VETASSIST AI - REPORTE DE CONSULTA CLINICA'), 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(120, 120, 120)
        clean_disclaimer = DISCLAIMER.replace("⚠️ **Aviso importante:** ", "")
        self.multi_cell(0, 3, sanitize_text(clean_disclaimer), 0, 'C')
        
        self.ln(2)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 5, sanitize_text(f'Pagina {self.page_no()}/{{nb}}'), 0, 0, 'C')

class ClinicalReportGenerator:
    """
    Genera reportes clínicos en PDF basados en la conversación e información del paciente.
    """
    def __init__(self, reports_dir: Path = REPORTS_DIR):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        paciente: dict,
        consulta_texto: str,
        recomendaciones: str,
        herramientas: list = None,
        fuentes: list = None,
        filename: str = ""
    ) -> str:
        """
        Genera el PDF y lo guarda en la carpeta de reportes.
        """
        if herramientas is None:
            herramientas = []
        if fuentes is None:
            fuentes = []
            
        pdf = VeterinaryReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Título del Reporte
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 10, sanitize_text("Informe Clinico de Soporte"), 0, 1, 'L')
        
        # Fecha y Hora
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(127, 140, 141)
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 5, sanitize_text(f"Generado el: {fecha_str}"), 0, 1, 'L')
        pdf.ln(5)

        # ----------------------------------------------------
        # Ficha del Paciente (Tabla estilizada)
        # ----------------------------------------------------
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(40, 116, 166)
        pdf.cell(0, 8, sanitize_text("1. DATOS DEL PACIENTE"), 0, 1, 'L')
        pdf.ln(2)

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(242, 244, 244)
        pdf.set_text_color(44, 62, 80)
        
        col_width = 38
        headers = ["Nombre", "Especie", "Raza", "Edad", "Peso (kg)"]
        for h in headers:
            pdf.cell(col_width, 7, sanitize_text(h), 1, 0, 'C', True)
        pdf.ln(7)

        pdf.set_font('Helvetica', '', 9)
        datos = [
            paciente.get("nombre", "N/A"),
            paciente.get("especie", "N/A").capitalize(),
            paciente.get("raza", "N/A"),
            paciente.get("edad", "N/A"),
            f"{paciente.get('peso', 'N/A')} kg"
        ]
        for d in datos:
            pdf.cell(col_width, 7, sanitize_text(str(d)), 1, 0, 'C')
        pdf.ln(12)

        # ----------------------------------------------------
        # Detalle de la Consulta
        # ----------------------------------------------------
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(40, 116, 166)
        pdf.cell(0, 8, sanitize_text("2. DETALLE Y MOTIVO DE CONSULTA"), 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 5, sanitize_text(consulta_texto))
        pdf.ln(8)

        # ----------------------------------------------------
        # Recomendaciones e Indicaciones
        # ----------------------------------------------------
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(40, 116, 166)
        pdf.cell(0, 8, sanitize_text("3. ANALISIS Y RECOMENDACIONES"), 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 5, sanitize_text(recomendaciones))
        pdf.ln(8)
        
        # (Secciones de Herramientas y Fuentes removidas por inestabilidad de FPDF con strings largos)

        # ----------------------------------------------------
        # Sección de Firma
        # ----------------------------------------------------
        pdf.ln(5)
        current_y = pdf.get_y()
        if current_y > 230: 
            pdf.add_page()
            
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(127, 140, 141)
        pdf.cell(95, 5, sanitize_text("Firma del Asistente IA (Soporte)"), 0, 0, 'C')
        pdf.cell(95, 5, sanitize_text("Firma del Veterinario a Cargo"), 0, 1, 'C')
        
        pdf.ln(12)
        pdf.cell(95, 5, "_______________________", 0, 0, 'C')
        pdf.cell(95, 5, "_______________________", 0, 1, 'C')
        
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(95, 5, "VetAssist AI Engine", 0, 0, 'C')
        pdf.cell(95, 5, sanitize_text("M.V. (Firma manuscrita)"), 0, 1, 'C')

        # Guardar Archivo
        if not filename:
            nombre_paciente = paciente.get("nombre", "paciente").lower().replace(" ", "_")
            filename = f"informe_{nombre_paciente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        target_path = self.reports_dir / filename
        pdf.output(str(target_path))
        
        return str(target_path.absolute())
