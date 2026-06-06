import logging
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    class FastMCP:
        """Fallback para permitir que Streamlit use las funciones sin el SDK MCP."""

        def __init__(self, name: str):
            self.name = name

        def tool(self):
            def decorator(func):
                return func
            return decorator

        def run(self, *args, **kwargs):
            raise RuntimeError(
                "El SDK oficial de MCP no esta instalado en este entorno. "
                "Instala las dependencias con: pip install -r requirements.txt"
            )

# Configurar logs hacia sys.stderr para no interferir con la comunicación stdio de JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("vet_mcp_server")

mcp = FastMCP("VetMCP")

@mcp.tool()
def calcular_dosis(medicamento: str, peso_kg: float, especie: str) -> str:
    """
    Calcula la dosis recomendada de medicamentos comunes para perros y gatos.
    
    Args:
        medicamento: Nombre del principio activo (meloxicam, amoxicilina, cefalexina, metronidazol).
        peso_kg: Peso del paciente en kilogramos.
        especie: Especie del paciente (perro / gato / canino / felino).
    """
    especie_norm = especie.lower().strip()
    if "gato" in especie_norm or "felin" in especie_norm:
        especie_norm = "gato"
    elif "perro" in especie_norm or "canin" in especie_norm:
        especie_norm = "perro"
    else:
        return f"Especie '{especie}' no soportada. Use 'perro' o 'gato'."

    med = medicamento.lower().strip()
    
    if peso_kg <= 0:
        return "El peso del paciente debe ser mayor a 0 kg."

    if "meloxicam" in med:
        # Perros: 0.2 mg/kg inicial, luego 0.1 mg/kg
        # Gatos: 0.1 mg/kg inicial, luego 0.05 mg/kg
        if especie_norm == "perro":
            dosis_inicial_mg = peso_kg * 0.2
            dosis_mantenimiento_mg = peso_kg * 0.1
            # Concentración habitual de suspensión oral: 1.5 mg/mL
            vol_inicial_ml = dosis_inicial_mg / 1.5
            vol_mantenimiento_ml = dosis_mantenimiento_mg / 1.5
            return (
                f"🩺 **Cálculo de Meloxicam para Perro ({peso_kg} kg):**\n"
                f"- **Dosis Inicial (Día 1 - 0.2 mg/kg):** {dosis_inicial_mg:.2f} mg "
                f"(Equivale a ~{vol_inicial_ml:.2f} mL de suspensión oral de 1.5 mg/mL)\n"
                f"- **Dosis de Mantenimiento (Día 2+ - 0.1 mg/kg):** {dosis_mantenimiento_mg:.2f} mg "
                f"(Equivale a ~{vol_mantenimiento_ml:.2f} mL)\n"
                f"⚠️ *Nota:* Administrar con alimento para prevenir problemas gastrointestinales."
            )
        else: # Gato
            dosis_inicial_mg = peso_kg * 0.1
            dosis_mantenimiento_mg = peso_kg * 0.05
            # Concentración habitual gatos: 0.5 mg/mL
            vol_inicial_ml = dosis_inicial_mg / 0.5
            vol_mantenimiento_ml = dosis_mantenimiento_mg / 0.5
            return (
                f"🩺 **Cálculo de Meloxicam para Gato ({peso_kg} kg):**\n"
                f"- **Dosis Inicial (Día 1 - 0.1 mg/kg):** {dosis_inicial_mg:.2f} mg "
                f"(Equivale a ~{vol_inicial_ml:.2f} mL de suspensión oral de 0.5 mg/mL)\n"
                f"- **Dosis de Mantenimiento (Día 2+ - 0.05 mg/kg):** {dosis_mantenimiento_mg:.2f} mg "
                f"(Equivale a ~{vol_mantenimiento_ml:.2f} mL)\n"
                f"⚠️ *Atención:* Uso limitado en gatos; no superar las dosis indicadas por riesgo renal."
            )

    elif "amoxicilina" in med:
        # Dosis estándar: 15 mg/kg cada 12 horas
        dosis_mg = peso_kg * 15
        # Supongamos suspensión de 250 mg/5 mL (50 mg/mL) o comprimidos de 250 mg / 500 mg
        vol_ml = dosis_mg / 50
        return (
            f"🩺 **Cálculo de Amoxicilina para {especie_norm.capitalize()} ({peso_kg} kg):**\n"
            f"- **Dosis recomendada (15 mg/kg):** {dosis_mg:.2f} mg cada 12 horas.\n"
            f"- **Presentación líquida (suspensión 50 mg/mL):** Administrar {vol_ml:.2f} mL por dosis.\n"
            f"- **Presentación sólida:** "
            f"{'Aproximadamente 1/4 comprimido de 250mg' if dosis_mg < 100 else '1 comprimido de 250mg' if dosis_mg < 350 else '1 comprimido de 500mg'} según criterio."
        )

    elif "cefalexina" in med:
        # Dosis estándar: 22 mg/kg cada 12 horas
        dosis_mg = peso_kg * 22
        # Supongamos suspensión de 250 mg/5 mL (50 mg/mL)
        vol_ml = dosis_mg / 50
        return (
            f"🩺 **Cálculo de Cefalexina para {especie_norm.capitalize()} ({peso_kg} kg):**\n"
            f"- **Dosis recomendada (22 mg/kg):** {dosis_mg:.2f} mg cada 12 horas.\n"
            f"- **Presentación líquida (suspensión 50 mg/mL):** Administrar {vol_ml:.2f} mL por dosis."
        )

    elif "metronidazol" in med:
        # Dosis estándar: 15 mg/kg cada 12 horas (infecciones bacterianas/giardia)
        dosis_mg = peso_kg * 15
        # Supongamos suspensión de 125 mg/5 mL (25 mg/mL)
        vol_ml = dosis_mg / 25
        return (
            f"🩺 **Cálculo de Metronidazol para {especie_norm.capitalize()} ({peso_kg} kg):**\n"
            f"- **Dosis recomendada (15 mg/kg):** {dosis_mg:.2f} mg cada 12 horas.\n"
            f"- **Presentación líquida (suspensión 25 mg/mL):** Administrar {vol_ml:.2f} mL por dosis.\n"
            f"⚠️ *Nota:* Medicamento con sabor muy amargo; puede provocar sialorrea en gatos."
        )

    else:
        return (
            f"Medicamento '{medicamento}' no parametrizado en la calculadora rápida.\n"
            f"Principios activos soportados: Meloxicam, Amoxicilina, Cefalexina, Metronidazol."
        )

@mcp.tool()
def consultar_vacunas(especie: str, edad_semanas: float) -> str:
    """
    Retorna el esquema de vacunación recomendado para un perro o gato según su edad en semanas.
    
    Args:
        especie: Especie del paciente (perro o gato).
        edad_semanas: Edad del paciente medida en semanas.
    """
    esp = especie.lower().strip()
    if "gato" in esp or "felin" in esp:
        esp = "gato"
    elif "perro" in esp or "canin" in esp:
        esp = "perro"
    else:
        return f"Especie '{especie}' no identificada. Use 'perro' o 'gato'."

    if edad_semanas < 0:
        return "La edad en semanas no puede ser negativa."

    if esp == "perro":
        if edad_semanas < 6:
            return "👶 **Paciente demasiado joven (< 6 semanas):** Aún tiene inmunidad materna residual. No requiere vacunas inmediatas salvo casos especiales de alto riesgo (Puppy DP)."
        elif 6 <= edad_semanas < 10:
            return (
                f"💉 **Esquema de Vacunación Canina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Primovacunación / Puppy DP (Parvovirus + Moquillo canino).\n"
                f"- **Próxima cita:** A las 10 semanas para vacuna Polivalente."
            )
        elif 10 <= edad_semanas < 14:
            return (
                f"💉 **Esquema de Vacunación Canina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Primera Dosis Polivalente (Parvovirus, Moquillo, Hepatitis, Leptospira, Adenovirus).\n"
                f"- **Próxima cita:** A las 14 semanas para el primer refuerzo Polivalente."
            )
        elif 14 <= edad_semanas < 16:
            return (
                f"💉 **Esquema de Vacunación Canina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Segundo Refuerzo Polivalente.\n"
                f"- **Próxima cita:** A las 16 semanas para vacuna de Rabia."
            )
        elif 16 <= edad_semanas < 52:
            return (
                f"💉 **Esquema de Vacunación Canina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Vacuna contra la Rabia + Refuerzo opcional de Tos de las perreras (Kennel Cough).\n"
                f"- **Próxima cita:** Refuerzo anual (Polivalente + Rabia) a partir del año de edad."
            )
        else:
            return (
                f"💉 **Esquema de Vacunación Canina (Adulto - {edad_semanas/4.3:.1f} meses):**\n"
                f"- **Vacuna requerida:** Refuerzo anual obligatorio (Polivalente + Rabia).\n"
                f"- **Frecuencia:** Cada 12 meses."
            )
            
    else: # Gato
        if edad_semanas < 8:
            return "👶 **Paciente demasiado joven (< 8 semanas):** Mantiene anticuerpos de la leche materna. No requiere vacunas inmediatas."
        elif 8 <= edad_semanas < 12:
            return (
                f"💉 **Esquema de Vacunación Felina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Primera dosis de la Triple Felina (Trivalente: Panleucopenia, Calicivirus y Rinotraqueítis).\n"
                f"- **Próxima cita:** A las 12 semanas para refuerzo y test de Leucemia Felina."
            )
        elif 12 <= edad_semanas < 16:
            return (
                f"💉 **Esquema de Vacunación Felina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Refuerzo de Triple Felina + Primera dosis de Leucemia Felina (previo test de descarte negativo).\n"
                f"- **Próxima cita:** A las 16 semanas para refuerzo de Leucemia y Rabia."
            )
        elif 16 <= edad_semanas < 52:
            return (
                f"💉 **Esquema de Vacunación Felina ({edad_semanas:.1f} semanas):**\n"
                f"- **Vacuna requerida:** Refuerzo de Leucemia Felina + Vacuna contra la Rabia.\n"
                f"- **Próxima cita:** Refuerzo anual a partir del año."
            )
        else:
            return (
                f"💉 **Esquema de Vacunación Felina (Adulto - {edad_semanas/4.3:.1f} meses):**\n"
                f"- **Vacuna requerida:** Refuerzo anual (Triple Felina + Leucemia Felina + Rabia).\n"
                f"- **Frecuencia:** Cada 12 meses."
            )

if __name__ == "__main__":
    logger.info("Iniciando el servidor VetMCP en modo stdio...")
    mcp.run(transport="stdio")
