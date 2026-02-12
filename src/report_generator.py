from fpdf import FPDF
import tempfile
from datetime import datetime

# COLORES CORPORATIVOS (RGB)
OXFORD_GRAY = (55, 65, 81)   # #374151
GOLD = (250, 204, 21)        # #FACC15
WHITE = (255, 255, 255)
LIGHT_GRAY = (243, 244, 246) # #F3F4F6

class PDF(FPDF):
    def header(self):
        # 1. FONDO ENCABEZADO (Gris Oxford)
        self.set_fill_color(*OXFORD_GRAY)
        self.rect(0, 0, 210, 40, 'F')
        
        # 2. LOGO Y TÍTULO (Dorado)
        self.set_y(10)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*GOLD)
        self.cell(0, 10, 'SAPRIA-FO', 0, 1, 'C')
        
        # 3. SUBTÍTULO (Blanco)
        self.set_font('Arial', '', 9)
        self.set_text_color(*WHITE)
        self.set_char_spacing(2) # Espaciado futurista
        self.cell(0, 5, 'REPORTE TÁCTICO DE MONITOREO MUNICIPAL', 0, 1, 'C')
        self.set_char_spacing(0)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Documento Oficial | Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        # Título de sección con línea dorada
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*OXFORD_GRAY)
        self.cell(0, 10, label, 0, 1, 'L')
        self.set_draw_color(*GOLD)
        self.set_line_width(1)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def metric_card(self, title, value, x, y):
        # Caja con borde dorado y fondo gris muy suave
        self.set_xy(x, y)
        self.set_fill_color(*LIGHT_GRAY)
        self.set_draw_color(*GOLD)
        self.rect(x, y, 85, 25, 'FD')
        
        # Título métrica
        self.set_xy(x + 5, y + 5)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(*OXFORD_GRAY)
        self.cell(80, 5, title, 0, 2)
        
        # Valor métrica
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*OXFORD_GRAY)
        self.cell(80, 10, str(value), 0, 0)

def generate_pdf_report(weather, fwi_cat, nasa_count, epicentros):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- SECCIÓN 1: RESUMEN DE SITUACIÓN ---
    pdf.chapter_title('ESTADO DE ALERTA EN TIEMPO REAL')
    
    # Fecha y Hora
    now = datetime.now().strftime("%d/%m/%Y %H:%M hrs")
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Fecha de Emisión: {now}', 0, 1)
    pdf.ln(5)

    # Métricas en cuadrícula (Diseño Futurista)
    temp = f"{weather['main']['temp']} °C" if weather else "--"
    hum = f"{weather['main']['humidity']} %" if weather else "--"
    
    # Fila 1 de Métricas
    y_start = pdf.get_y()
    pdf.metric_card("TEMPERATURA ACTUAL", temp, 10, y_start)
    pdf.metric_card("HUMEDAD RELATIVA", hum, 105, y_start)
    
    # Fila 2 de Métricas
    y_start += 30
    pdf.metric_card("ÍNDICE DE RIESGO FWI", fwi_cat, 10, y_start)
    pdf.metric_card("ANOMALÍAS TÉRMICAS (NASA)", str(nasa_count), 105, y_start)
    
    pdf.ln(40)

    # --- SECCIÓN 2: ANÁLISIS DE INTELIGENCIA (K-MEANS) ---
    pdf.chapter_title('ZONAS CRÍTICAS IDENTIFICADAS (IA)')
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "El sistema de inteligencia artificial ha detectado las siguientes zonas de alta concentración histórica de incidentes, lo que sugiere una alta probabilidad de reincidencia:")
    pdf.ln(5)

    if epicentros:
        # Encabezado de tabla personalizado
        pdf.set_fill_color(*OXFORD_GRAY)
        pdf.set_text_color(*GOLD)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(30, 10, 'ZONA ID', 1, 0, 'C', True)
        pdf.cell(100, 10, 'NIVEL DE PELIGROSIDAD', 1, 0, 'C', True)
        pdf.cell(60, 10, 'ESTADO', 1, 1, 'C', True)

        # Filas de tabla
        pdf.set_text_color(50, 50, 50)
        pdf.set_font('Arial', '', 10)
        for ep in epicentros[:5]:
            pdf.cell(30, 10, str(ep['id']), 1, 0, 'C')
            pdf.cell(100, 10, f"Concentración: {ep['weight']}", 1, 0, 'C')
            pdf.set_font('Arial', 'B', 10)
            if ep['peligro'] == "CRÍTICO":
                pdf.set_text_color(220, 50, 50) # Rojo para crítico
            else:
                pdf.set_text_color(50, 50, 50)
            pdf.cell(60, 10, ep['peligro'], 1, 1, 'C')
            pdf.set_text_color(50, 50, 50) # Reset color
            pdf.set_font('Arial', '', 10)
    else:
        pdf.cell(0, 10, "No se detectaron clusters de riesgo activos.", 0, 1)

    pdf.ln(10)
    
    # --- SECCIÓN 3: RECOMENDACIONES ---
    pdf.chapter_title('PROTOCOLOS DE ACCIÓN RECOMENDADOS')
    pdf.set_font('Arial', '', 10)
    recomendaciones = [
        "1. Desplegar unidades de patrullaje preventivo en las Zonas Críticas identificadas.",
        "2. Mantener monitoreo satelital continuo (frecuencia 15 min).",
        "3. Verificar disponibilidad de recursos hídricos cercanos a los puntos de calor.",
        "4. Emitir alerta preventiva a las estaciones de bomberos del sector sur."
    ]
    for rec in recomendaciones:
        pdf.cell(0, 8, rec, 0, 1)

    # Guardar en archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name