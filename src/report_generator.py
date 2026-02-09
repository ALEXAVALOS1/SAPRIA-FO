from fpdf import FPDF
import pandas as pd
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        # Fondo oscuro para el header (simulando banda institucional)
        self.set_fill_color(11, 17, 33) # Color oscuro del tema
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_font('Arial', 'B', 24)
        self.set_text_color(225, 29, 72) # Rojo SAPRIA
        self.cell(0, 15, 'SAPRIA-FO', 0, 1, 'C', False)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 5, 'SISTEMA DE ALERTA TEMPRANA - CIUDAD JUAREZ', 0, 1, 'C', False)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Pagina {self.page_no()} - Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')

def generate_pdf_report(df_incendios, weather_data, aqi_data):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Resumen Ejecutivo
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(11, 17, 33)
    pdf.cell(0, 10, '1. RESUMEN OPERATIVO ACTUAL', 0, 1, 'L')
    pdf.ln(5)

    pdf.set_font('Arial', '', 11)
    # Datos del Clima
    temp = weather_data['main']['temp'] if weather_data else "N/A"
    hum = weather_data['main']['humidity'] if weather_data else "N/A"
    aqi = aqi_data['texto'] if aqi_data else "N/A"
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(60, 10, f'Temperatura: {temp} C', 1, 0, 'C', 1)
    pdf.cell(60, 10, f'Humedad: {hum}%', 1, 0, 'C', 1)
    pdf.cell(60, 10, f'Calidad Aire: {aqi}', 1, 1, 'C', 1)
    pdf.ln(10)

    # 2. Análisis de Incidentes
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '2. INCIDENTES REGISTRADOS', 0, 1, 'L')
    pdf.ln(5)
    
    if not df_incendios.empty:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(225, 29, 72)
        pdf.set_text_color(255, 255, 255)
        # Encabezados de tabla
        pdf.cell(40, 10, 'FECHA', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'ZONA/COLONIA', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'TIPO', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'ESTATUS', 1, 1, 'C', 1)
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(0)
        
        # Filas (Últimos 10)
        for index, row in df_incendios.head(10).iterrows():
            fecha = row['fecha'].strftime('%Y-%m-%d')
            colonia = str(row['colonia'])[:25]
            tipo = str(row['tipo_incidente'])[:25]
            pdf.cell(40, 8, fecha, 1)
            pdf.cell(50, 8, colonia, 1)
            pdf.cell(50, 8, tipo, 1)
            pdf.cell(50, 8, 'Atendido', 1, 1)
    else:
        pdf.cell(0, 10, 'No hay datos de incidentes disponibles.', 0, 1)

    # 3. Recomendaciones
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '3. ACCIONES RECOMENDADAS', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    recomendaciones = [
        "- Mantener vigilancia satelital activa en zona poniente.",
        "- Verificar operatividad de hidrantes en colonias marcadas.",
        "- Emitir boletín preventivo si la humedad baja del 15%."
    ]
    
    for rec in recomendaciones:
        pdf.cell(0, 8, rec, 0, 1)

    # Retornar el PDF como string binario
    return pdf.output(dest='S').encode('latin-1', 'replace') # Codificación segura