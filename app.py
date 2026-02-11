import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap, AntPath
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SINAPRIA-FO | Oxford Gray", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except: pass
local_css("assets/style.css")

try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_nasa_firms_data, find_nearest_station, get_route_osrm
    from src.components import inject_tailwind, render_left_alert_card, render_factors_card, render_right_metrics, render_log_card, render_forecast_section, render_footer
    from src.fwi_calculator import calculate_fwi
    from src.ml_engine import get_risk_clusters
    from src.report_generator import generate_pdf_report
    from src.analytics import render_3d_density_map, render_statistics 
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

inject_tailwind()

# --- 2. DATOS ---
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 

@st.cache_data(ttl=600)
def get_data_bundle():
    df = load_historical_data("incendios.csv")
    weather = get_weather_data(JUAREZ_LAT, JUAREZ_LON)
    df_infra = get_real_infrastructure(JUAREZ_LAT, JUAREZ_LON, radius=10000)
    df_nasa = get_nasa_firms_data()
    return df, weather, df_infra, df_nasa

df, weather, df_infra, df_nasa = get_data_bundle()
epicentros_ia = get_risk_clusters(df, num_clusters=5)

sim_wind = weather['wind']['speed'] * 3.6 if weather else 20
sim_temp = weather['main']['temp'] if weather else 30
sim_hum = weather['main']['humidity'] if weather else 20
fwi_val, fwi_cat, fwi_col = calculate_fwi(sim_temp, sim_hum, sim_wind)

# ==============================================================================
# ENCABEZADO Y NAVEGACIÓN (BARRA OXFORD GRAY DE EXTREMO A EXTREMO)
# ==============================================================================
col_logo, col_nav = st.columns([1, 2])

# LOGO A LA IZQUIERDA (DORADO)
with col_logo:
    st.markdown("""
    <div style="color: #FACC15; font-size: 32px; font-weight: 900; line-height: 1.1; margin-top: -8px;">
        SAPRIA-FO
        <div style="color: #FFFFFF; font-size: 11px; font-weight: 600; letter-spacing: 2px;">
            MONITOREO MUNICIPAL
        </div>
    </div>
    """, unsafe_allow_html=True)

# BOTONES CARGADOS A LA DERECHA (DORADOS)
with col_nav:
    opciones_nav = ["🗺️ Dashboard Táctico", "📊 Base de Datos Histórica", "🚨 Analítica 3D Avanzada"]
    seleccion = st.radio("Menú", opciones_nav, horizontal=True, label_visibility="collapsed")

if "Dashboard" in seleccion: pagina_actual = "Dashboard"
elif "Base" in seleccion: pagina_actual = "Base"
elif "Analítica" in seleccion: pagina_actual = "Analitica"

# Contenedor Principal (Debajo de la barra, con margen para respirar)
st.markdown('<div class="container mx-auto px-4 py-8 mt-4">', unsafe_allow_html=True)

# ==============================================================================
# PANTALLA 1: DASHBOARD PRINCIPAL
# ==============================================================================
if pagina_actual == "Dashboard":
    col_izq, col_mapa, col_der = st.columns([2.5, 6.5, 3], gap="medium")

    with col_izq:
        render_left_alert_card(len(df_nasa))
        render_factors_card(weather, fwi_cat)
        st.markdown('<div class="bg-card-light rounded-xl shadow-sm p-4 border border-gray-100"><h2 class="font-bold text-gray-800 flex items-center gap-2 text-xs uppercase tracking-wider mb-3"><span class="material-icons-outlined text-primary text-sm">tune</span> Capas de Monitoreo</h2></div>', unsafe_allow_html=True)
        
        show_heatmap = st.toggle("🔥 Historial Térmico", value=True)
        show_ai = st.toggle("🧠 Zonas K-Means (IA)", value=True)
        show_infra = st.toggle("🏭 Infraestructura Civil", value=False)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 GENERAR REPORTE PDF", type="primary", use_container_width=True):
            with st.spinner("Compilando PDF..."):
                try:
                    pdf_path = generate_pdf_report(weather, fwi_cat, len(df_nasa), epicentros_ia)
                    with open(pdf_path, "rb") as f:
                        st.download_button("⬇️ DESCARGAR", data=f, file_name="Reporte_SINAPRIA.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e: st.error("Error PDF")

    with col_mapa:
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=11, tiles="CartoDB positron")
        
        if show_heatmap and not df.empty: HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#FACC15', 1:'#EF4444'}).add_to(m)
        if show_infra and not df_infra.empty:
            for _, r in df_infra.iterrows():
                ic = 'truck-medical' if r['tipo']=='Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], tooltip=r['nombre'], icon=folium.Icon(color="lightgray", icon_color=r['color'], icon=ic, prefix="fa")).add_to(m)
        if not df_nasa.empty:
            for _, r in df_nasa.iterrows():
                folium.CircleMarker(location=[r['latitude'], r['longitude']], radius=10, color="#EF4444", fill=True, fill_color="#EF4444", fill_opacity=0.7).add_to(m)
        if show_ai:
            for ep in epicentros_ia:
                color = "#EF4444" if ep['peligro'] == "CRÍTICO" else "#FACC15"
                folium.Circle(location=[ep['lat'], ep['lon']], radius=1500, color=color, weight=1, fill=True, fill_opacity=0.1).add_to(m)

        if st.session_state['sim_coords']:
            sim_lat, sim_lon = st.session_state['sim_coords']['lat'], st.session_state['sim_coords']['lng']
            folium.Marker([sim_lat, sim_lon], icon=folium.Icon(color="red", icon="fire", prefix="fa")).add_to(m)
            nearest = find_nearest_station(sim_lat, sim_lon, df_infra)
            if nearest is not None:
                folium.Marker([nearest['lat'], nearest['lon']], tooltip=nearest['nombre'], icon=folium.Icon(color="blue", icon="truck-medical", prefix="fa")).add_to(m)
                route = get_route_osrm(nearest['lat'], nearest['lon'], sim_lat, sim_lon)
                if route: AntPath(locations=route['path'], color="#374151", weight=5, opacity=0.8, delay=800).add_to(m)

        map_data = st_folium(m, width="100%", height=530)
        if map_data['last_clicked'] and st.session_state['sim_coords'] != map_data['last_clicked']:
            st.session_state['sim_coords'] = map_data['last_clicked']; st.rerun()

        # PRONÓSTICO DINÁMICO (Con temperatura real en vivo)
        render_forecast_section(sim_temp)

    with col_der:
        render_right_metrics(len(df) if not df.empty else 0)
        render_log_card(epicentros_ia)

# ==============================================================================
# PANTALLA 2: BASE DE DATOS
# ==============================================================================
elif pagina_actual == "Base":
    st.markdown("<h2 class='text-2xl font-bold text-gray-800 mb-2'>Base de Datos Histórica</h2><p class='text-gray-500 mb-6'>Registro completo de incidentes detectados en el área metropolitana.</p>", unsafe_allow_html=True)
    if not df.empty:
        df_limpio = df[['fecha', 'colonia', 'tipo_incidente', 'causa', 'dano']].copy()
        df_limpio['fecha'] = pd.to_datetime(df_limpio['fecha']).dt.strftime('%Y-%m-%d')
        # Tabla limpia sin índice
        st.dataframe(df_limpio, use_container_width=True, hide_index=True, height=600)

# ==============================================================================
# PANTALLA 3: ANALÍTICA AVANZADA
# ==============================================================================
elif pagina_actual == "Analitica":
    st.markdown("<h2 class='text-2xl font-bold text-gray-800 mb-2'>Analítica Volumétrica 3D</h2><p class='text-gray-500 mb-6'>Proyección espacial y estadísticas de zonas calientes.</p>", unsafe_allow_html=True)
    render_3d_density_map(df)
    st.markdown("<hr class='my-8 border-gray-200'>", unsafe_allow_html=True)
    render_statistics(df)


st.markdown('</div>', unsafe_allow_html=True)
render_footer()