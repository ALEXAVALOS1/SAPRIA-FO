from fpdf import FPDF
from datetime import datetime
import tempfile

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(225, 29, 72) # Rojo Sapria
        self.cell(0, 10, 'SAPRIA-FO: INFORME TACTICO OFICIAL', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 10, f'Generado por Inteligencia Artificial - {fecha_actual}', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(weather, fwi_cat, nasa_alerts, clusters):
    """Genera un PDF con el resumen táctico del sistema."""
    pdf = PDF()
    pdf.add_page()
    
    # --- 1. CLIMA ---
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, '1. CONDICIONES METEOROLOGICAS ACTUALES', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    temp = weather['main']['temp'] if weather else 'N/A'
    hum = weather['main']['humidity'] if weather else 'N/A'
    wind = weather['wind']['speed'] * 3.6 if weather else 0
    
    pdf.cell(0, 8, f'  - Temperatura: {temp} C', 0, 1)
    pdf.cell(0, 8, f'  - Humedad: {hum}%', 0, 1)
    pdf.cell(0, 8, f'  - Viento: {wind:.1f} km/h', 0, 1)
    pdf.ln(5)

    # --- 2. ALERTAS ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. ESTADO DE RIESGO Y MONITOREO SATELITAL (NASA)', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f'  - Indice de Riesgo (FWI): NIVEL {fwi_cat}', 0, 1)
    pdf.cell(0, 8, f'  - Anomalias Termicas Satelitales (24h): {nasa_alerts} detectadas', 0, 1)
    pdf.ln(5)

    # --- 3. INTELIGENCIA ARTIFICIAL ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. PREDICCION DE INTELIGENCIA ARTIFICIAL (ZONAS CRITICAS)', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    if clusters:
        for c in clusters[:3]: # Solo el Top 3
            pdf.cell(0, 8, f'  - Epicentro {c["id"]} | Nivel: {c["peligro"]} | Historial: {c["weight"]} eventos', 0, 1)
    else:
        pdf.cell(0, 8, '  - No hay datos suficientes para prediccion.', 0, 1)

    pdf.ln(15)
    
    # --- DISCLAIMER ---
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    disclaimer = "Este documento es estrictamente confidencial y generado de forma autonoma por el Sistema Municipal de Alertamiento Temprano (SAPRIA-FO). Las zonas marcadas representan calculos estadisticos."
    pdf.multi_cell(0, 6, disclaimer)

    # Guardar en archivo temporal
    tmp_filename = tempfile.mktemp(suffix='.pdf')
    pdf.output(tmp_filename)
    return tmp_filename