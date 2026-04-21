import os
import math
import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# --- FÓRMULA MATEMÁTICA PARA DISTANCIAS GPS ---
def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en metros entre dos coordenadas GPS"""
    R = 6371000 # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- CLASE DEL REPORTE (DISEÑO OFICIAL) ---
class URBIPREXProReport(FPDF):
    def header(self):
        self.set_fill_color(11, 28, 20) 
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(74, 222, 128)
        self.cell(0, 10, 'URBIPREX: REPORTE TACTICO DE INTELIGENCIA', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, 'Sistema de Analisis Predictivo de Riesgos de Incendios Urbanos', 0, 1, 'L')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Documento Oficial - Proteccion Civil Municipal - Pagina {self.page_no()}', 0, 0, 'C')

    def section_title(self, title):
        self.ln(6)
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(26, 53, 37)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', fill=True)
        self.ln(4)

# --- GENERADOR DE GRÁFICAS ---
def generar_grafica_radar(datos, filename="temp_chart.png"):
    """Genera una gráfica de barras de impacto visual"""
    labels = ['Densidad Vial', 'Cruces Peligrosos', 'Aislamiento (Bomberos)', 'Historial Incendios']
    valores = [
        min(datos.get('densidad_vial', 0) * 2, 100), 
        min(datos.get('intersecciones_km2', 0) * 1.5, 100), 
        min(datos.get('acceso_bomberos_km', 0) * 20, 100), 
        min(datos.get('total_incendios', 0) * 25, 100)
    ]
    
    plt.figure(figsize=(8, 4))
    plt.style.use('dark_background')
    fig = plt.gcf()
    fig.patch.set_facecolor('#0b1c14')
    ax = plt.gca()
    ax.set_facecolor('#0b1c14')
    
    # Colores semáforo según la gravedad
    colores = ['#ef4444' if v > 70 else '#facc15' if v > 40 else '#4ade80' for v in valores]
    
    plt.barh(labels, valores, color=colores, height=0.6)
    plt.title('INDICE DE VULNERABILIDAD (0 - 100%)', color='white', fontsize=12, pad=15, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#1f402d')
    ax.spines['left'].set_color('#1f402d')
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    return filename

# --- FUNCIÓN PRINCIPAL ---
def generar_reporte_real():
    print("🔍 Analizando inteligencia de datos y recursos hídricos...")
    
    # 1. LEER DATOS REALES DE LA MANZANA
    df = pd.read_csv("data/outputs/dataset_final.csv")
    df_riesgo = df.sort_values(by=['total_incendios', 'acceso_bomberos_km'], ascending=[False, False])
    manzana = df_riesgo.iloc[0].to_dict()
    
    # 2. CALCULAR HIDRANTES CERCANOS (NUEVO)
    total_hidrantes_cercanos = 0
    try:
        with open("public/data/hidrantes.json", 'r', encoding='utf-8') as f:
            hidrantes = json.load(f)
            # Como el CSV no tiene lat/lon directo de la manzana, usamos el centro de Juárez como referencia aproximada
            # (En la fase 3 cruzaremos esto exactamente por manzana, por ahora hacemos un cálculo base)
            lat_ref, lon_ref = 31.7333, -106.4833 
            for h in hidrantes:
                dist = calcular_distancia_haversine(lat_ref, lon_ref, h['lat'], h['lon'])
                if dist <= 800: # 800 metros de radio
                    total_hidrantes_cercanos += 1
    except Exception as e:
        print(f"⚠️ Nota: No se pudo cruzar con hidrantes: {e}")

    # 3. CREAR PDF
    pdf = URBIPREXProReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # --- PORTADA TÁCTICA ---
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 22)
    pdf.set_text_color(220, 38, 38) # Rojo Alerta
    pdf.cell(0, 10, f"ALERTA PREDICTIVA: MANZANA {manzana.get('CVEGEO')}", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(45, 55, 72)
    pdf.cell(0, 8, f"NIVEL DE RIESGO: CRITICO (Prioridad Nivel 1)", 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generado el: {fecha_hoy} | URBIPREX Core v2.0", 0, 1, 'C')
    pdf.ln(2)

    # --- SECCIÓN 1: VULNERABILIDAD ESTRUCTURAL ---
    pdf.section_title("1. PERFIL DE VULNERABILIDAD ESTRUCTURAL")
    
    # Usamos posiciones XY para hacer 2 columnas
    y_actual = pdf.get_y()
    
    # Columna Izquierda (Datos)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(90, 7, "Métricas Espaciales (Semana 6):", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(90, 7, f" - Historial Incidentes: {int(manzana.get('total_incendios', 0))} registros", 0, 1)
    pdf.cell(90, 7, f" - Distancia a Bomberos: {manzana.get('acceso_bomberos_km', 0):.2f} km", 0, 1)
    pdf.cell(90, 7, f" - Densidad Vial: {manzana.get('densidad_vial', 0):.2f} km/km2", 0, 1)
    pdf.cell(90, 7, f" - Vias Principales: {manzana.get('tipo_vial_pct', 0):.1f}%", 0, 1)
    
    # Columna Derecha (Recursos)
    pdf.set_xy(110, y_actual)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 7, "Recursos Operativos Cercanos:", 0, 1)
    pdf.set_xy(110, pdf.get_y())
    pdf.set_font('Arial', '', 10)
    pdf.cell(90, 7, f" - Hidrantes en radio 800m: {total_hidrantes_cercanos} unidades", 0, 1)
    pdf.set_xy(110, pdf.get_y())
    pdf.cell(90, 7, f" - Tiempo est. de arribo: {int(manzana.get('acceso_bomberos_km', 0) * 1.5)} minutos", 0, 1)
    
    pdf.ln(10)

    # --- SECCIÓN 2: GRÁFICA DE IMPACTO ---
    pdf.section_title("2. MATRIZ DE RIESGOS PONDERADA")
    grafica_temp = generar_grafica_radar(manzana)
    pdf.image(grafica_temp, x=15, w=180)
    pdf.ln(5)

    # --- SECCIÓN 3: DIRECTRICES DE ACCIÓN ---
    pdf.section_title("3. PROTOCOLO DE ACCION SUGERIDO")
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(30, 30, 30)
    
    pdf.multi_cell(0, 6, "1. INMEDIATA: Desplegar unidad de inspeccion preventiva a la zona debido a la alta combinacion de densidad vial y lejanía de la estacion central.\n\n2. RECURSOS HIDRICOS: Se identificaron hidrantes en la periferia. Validar presion de agua en el sector con la Junta Municipal de Agua y Saneamiento (JMAS).\n\n3. MONITOREO: Mantener alerta en el dashboard URBIPREX si la velocidad del viento supera los 30 km/h o la temperatura los 35 C.")

    # --- GUARDAR ARCHIVO ---
    os.makedirs("public/data/reportes", exist_ok=True)
    filename = f"public/data/reportes/URBIPREX_Tactica_{manzana.get('CVEGEO')}.pdf"
    pdf.output(filename)
    
    if os.path.exists(grafica_temp):
        os.remove(grafica_temp)
        
    print(f"✅ ¡Reporte Maestro generado con análisis de hidrantes y diseño a 2 columnas!")
    print(f"📁 Revísalo en: {filename}")

if __name__ == "__main__":
    generar_reporte_real()