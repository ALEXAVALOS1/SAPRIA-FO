from fpdf import FPDF
import tempfile
from datetime import datetime

# COLORES CORPORATIVOS
OXFORD_GRAY = (55, 65, 81)   # #374151
GOLD = (250, 204, 21)        # #FACC15
WHITE = (255, 255, 255)
TEXT_GRAY = (100, 100, 100)

class PDF(FPDF):
    def header(self):
        # Fondo Encabezado
        self.set_fill_color(*OXFORD_GRAY)
        self.rect(0, 0, 210, 40, 'F')
        # Logo y Título
        self.set_y(12)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*GOLD)
        self.cell(0, 10, 'SAPRIA-FO', 0, 1, 'C')
        # Subtítulo
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*WHITE)
        self.cell(0, 5, 'REPORTE TACTICO DE MONITOREO MUNICIPAL', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Documento Oficial | Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*OXFORD_GRAY)
        self.cell(0, 8, label, 0, 1, 'L')
        self.set_draw_color(*GOLD)
        self.set_line_width(1.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def metric_card(self, title, value, x, y):
        self.set_xy(x, y)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(*OXFORD_GRAY)
        self.set_line_width(0.5)
        self.rect(x, y, 85, 25, 'FD')
        # Indicador lateral dorado
        self.set_fill_color(*GOLD)
        self.rect(x, y, 2, 25, 'F')
        # Título
        self.set_xy(x + 5, y + 5)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(150, 150, 150)
        self.cell(80, 5, title, 0, 2)
        # Valor
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*OXFORD_GRAY)
        self.cell(80, 10, str(value), 0, 0)

def generate_pdf_report(weather, fwi_cat, nasa_count, epicentros, total_historico):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- DATOS DEL CLIMA ---
    temp = f"{weather['main']['temp']} C" if weather else "--"
    hum = f"{weather['main']['humidity']} %" if weather else "--"
    wind_spd = f"{weather['wind']['speed']*3.6:.1f} km/h" if weather else "--" # Convertimos m/s a km/h
    wind_deg = f"{weather['wind']['deg']} Grados" if weather else "--"

    # --- SECCIÓN 1: RESUMEN METEOROLÓGICO Y RIESGO ---
    pdf.chapter_title('ESTADO DE ALERTA EN TIEMPO REAL')
    
    now = datetime.now().strftime("%d/%m/%Y %H:%M hrs")
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(*TEXT_GRAY)
    pdf.cell(0, 10, f'Fecha de Emision: {now}', 0, 1)
    pdf.ln(5)

    y_start = pdf.get_y()
    
    # Fila 1
    pdf.metric_card("TEMPERATURA ACTUAL", temp, 10, y_start)
    pdf.metric_card("HUMEDAD RELATIVA", hum, 105, y_start)
    
    # Fila 2
    y_start += 30
    pdf.metric_card("VELOCIDAD DEL VIENTO", wind_spd, 10, y_start)
    pdf.metric_card("DIRECCION DEL VIENTO", wind_deg, 105, y_start)

    # Fila 3 (Riesgos)
    y_start += 30
    pdf.metric_card("INDICE DE RIESGO FWI", fwi_cat, 10, y_start)
    pdf.metric_card("ANOMALIAS NASA (24H)", str(nasa_count), 105, y_start)
    
    pdf.ln(35)

    # --- SECCIÓN 2: ESTADÍSTICA HISTÓRICA ---
    pdf.chapter_title('ANALISIS HISTORICO')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Total de incidentes registrados en la base de datos historica: {total_historico}", 0, 1)
    pdf.ln(5)

    # --- SECCIÓN 3: ZONAS CRÍTICAS ---
    pdf.chapter_title('ZONAS CRITICAS IDENTIFICADAS (IA)')
    
    if epicentros:
        # Encabezado
        pdf.set_fill_color(*OXFORD_GRAY)
        pdf.set_text_color(*GOLD)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 10, 'ZONA ID', 1, 0, 'C', True)
        pdf.cell(90, 10, 'CONCENTRACION', 1, 0, 'C', True)
        pdf.cell(60, 10, 'NIVEL', 1, 1, 'C', True)

        # Datos
        pdf.set_text_color(50, 50, 50)
        pdf.set_font('Arial', '', 10)
        for ep in epicentros[:5]:
            pdf.cell(40, 10, str(ep['id']), 1, 0, 'C')
            pdf.cell(90, 10, f"{ep['weight']} Eventos", 1, 0, 'C')
            if ep['peligro'] in ["CRITICO", "ALTO"]:
                pdf.set_text_color(220, 50, 50)
                pdf.set_font('Arial', 'B', 10)
            else:
                pdf.set_text_color(50, 50, 50)
                pdf.set_font('Arial', '', 10)
            pdf.cell(60, 10, ep['peligro'], 1, 1, 'C')
            # Reset
            pdf.set_text_color(50, 50, 50)
            pdf.set_font('Arial', '', 10)
    else:
        pdf.cell(0, 10, "Sin clusters de riesgo activos.", 0, 1)

    pdf.ln(10)

    # Output
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name