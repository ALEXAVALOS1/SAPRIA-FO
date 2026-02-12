from fpdf import FPDF
import tempfile
from datetime import datetime

# COLORES CORPORATIVOS (RGB)
OXFORD_GRAY = (55, 65, 81)   # #374151
GOLD = (250, 204, 21)        # #FACC15
WHITE = (255, 255, 255)
LIGHT_GRAY = (243, 244, 246) # #F3F4F6
TEXT_GRAY = (100, 100, 100)

class PDF(FPDF):
    def header(self):
        # 1. FONDO ENCABEZADO (Gris Oxford Sólido)
        self.set_fill_color(*OXFORD_GRAY)
        self.rect(0, 0, 210, 40, 'F')
        
        # 2. LOGO Y TÍTULO (Dorado)
        self.set_y(12)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*GOLD)
        self.cell(0, 10, 'SAPRIA-FO', 0, 1, 'C')
        
        # 3. SUBTÍTULO (Blanco)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*WHITE)
        # Eliminamos set_char_spacing para evitar el error
        self.cell(0, 5, 'REPORTE TACTICO DE MONITOREO MUNICIPAL', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Documento Oficial | Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        # Título de sección con línea dorada gruesa
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*OXFORD_GRAY)
        self.cell(0, 8, label, 0, 1, 'L')
        self.set_draw_color(*GOLD)
        self.set_line_width(1.5) # Línea más gruesa para estilo futurista
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def metric_card(self, title, value, x, y):
        # Tarjeta de métrica estilo "HUD"
        self.set_xy(x, y)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(*OXFORD_GRAY)
        self.set_line_width(0.5)
        self.rect(x, y, 85, 25, 'FD')
        
        # Borde izquierdo dorado (indicador de estado)
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

def generate_pdf_report(weather, fwi_cat, nasa_count, epicentros):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- SECCIÓN 1: RESUMEN DE SITUACIÓN ---
    pdf.chapter_title('ESTADO DE ALERTA EN TIEMPO REAL')
    
    # Fecha y Hora
    now = datetime.now().strftime("%d/%m/%Y %H:%M hrs")
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(*TEXT_GRAY)
    pdf.cell(0, 10, f'Fecha de Emision: {now}', 0, 1)
    pdf.ln(5)

    # Preparar datos
    temp = f"{weather['main']['temp']} C" if weather else "--"
    hum = f"{weather['main']['humidity']} %" if weather else "--"
    
    # Dibujar Tarjetas (Grid 2x2)
    y_start = pdf.get_y()
    
    # Fila 1
    pdf.metric_card("TEMPERATURA ACTUAL", temp, 10, y_start)
    pdf.metric_card("HUMEDAD RELATIVA", hum, 105, y_start)
    
    # Fila 2
    y_start += 32
    pdf.metric_card("INDICE DE RIESGO FWI", fwi_cat, 10, y_start)
    pdf.metric_card("ANOMALIAS TERMICAS (NASA)", str(nasa_count), 105, y_start)
    
    pdf.ln(45)

    # --- SECCIÓN 2: ANÁLISIS DE INTELIGENCIA ---
    pdf.chapter_title('ZONAS CRITICAS IDENTIFICADAS (IA)')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(*TEXT_GRAY)
    pdf.multi_cell(0, 5, "El sistema de inteligencia artificial ha detectado las siguientes zonas de alta concentracion historica de incidentes:")
    pdf.ln(5)

    if epicentros:
        # Encabezado Tabla
        pdf.set_fill_color(*OXFORD_GRAY)
        pdf.set_text_color(*GOLD)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 10, 'ZONA ID', 1, 0, 'C', True)
        pdf.cell(90, 10, 'CONCENTRACION', 1, 0, 'C', True)
        pdf.cell(60, 10, 'NIVEL', 1, 1, 'C', True)

        # Datos Tabla
        pdf.set_text_color(50, 50, 50)
        pdf.set_font('Arial', '', 10)
        for ep in epicentros[:5]:
            pdf.cell(40, 10, str(ep['id']), 1, 0, 'C')
            pdf.cell(90, 10, f"{ep['weight']} Eventos Hist.", 1, 0, 'C')
            
            # Color condicional para el nivel
            if ep['peligro'] == "CRITICO" or ep['peligro'] == "ALTO":
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
        pdf.cell(0, 10, "No se detectaron clusters de riesgo activos.", 0, 1)

    pdf.ln(10)
    
    # --- SECCIÓN 3: RECOMENDACIONES ---
    pdf.chapter_title('PROTOCOLOS DE ACCION')
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(*TEXT_GRAY)
    recomendaciones = [
        "1. Desplegar unidades de patrullaje preventivo en las Zonas Criticas.",
        "2. Mantener monitoreo satelital continuo (frecuencia 15 min).",
        "3. Verificar disponibilidad de recursos hidricos cercanos.",
        "4. Emitir alerta preventiva a las estaciones de bomberos del sector."
    ]
    for rec in recomendaciones:
        pdf.cell(0, 8, rec, 0, 1)

    # Output
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name