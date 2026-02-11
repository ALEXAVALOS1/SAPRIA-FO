import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SAPRIA-FO", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# Cargar CSS
def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except: pass
local_css("assets/style.css")

# Importaciones
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_nasa_firms_data
    from src.navbar import render_navbar # IMPORTAMOS EL NAVBAR
    from src.components import inject_tailwind, render_left_alert_card, render_factors_card, render_right_metrics, render_log_card, render_forecast_section, render_footer
    from src.fwi_calculator import calculate_fwi
    from src.ml_engine import get_risk_clusters
    from src.report_generator import generate_pdf_report
    from src.analytics import render_3d_density_map
except ImportError as e:
    st.error(f"Error crítico: {e}")
    st.stop()

inject_tailwind()

# Datos
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 
@st.cache_data(ttl=600)
def get_data_bundle():
    df = load_historical_data("incendios.csv")
    weather = get_weather_data(JUAREZ_LAT, JUAREZ_LON)
    df_nasa = get_nasa_firms_data()
    return df, weather, df_nasa

df, weather, df_nasa = get_data_bundle()
epicentros_ia = get_risk_clusters(df, num_clusters=5)
sim_wind = weather['wind']['speed'] * 3.6 if weather else 20
sim_temp = weather['main']['temp'] if weather else 30
sim_hum = weather['main']['humidity'] if weather else 20
fwi_val, fwi_cat, fwi_col = calculate_fwi(sim_temp, sim_hum, sim_wind)

# 1. RENDERIZAR BARRA
pagina_actual, btn_reporte = render_navbar()

if btn_reporte:
    with st.spinner("Generando PDF..."):
        generate_pdf_report(weather, fwi_cat, len(df_nasa), epicentros_ia)
        st.toast("Reporte Generado")

# 2. CONTENIDO
st.markdown('<div class="container mx-auto px-4">', unsafe_allow_html=True)

if pagina_actual == "Dashboard":
    col_izq, col_mapa, col_der = st.columns([2.5, 6.5, 3], gap="medium")
    
    with col_izq:
        render_left_alert_card(len(df_nasa))
        render_factors_card(weather, fwi_cat)
        show_heatmap = st.toggle("🔥 Historial", value=True)
        show_ai = st.toggle("🧠 Zonas IA", value=True)

    with col_mapa:
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=11, tiles="CartoDB positron")
        if show_heatmap and not df.empty: HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#FACC15', 1:'#EF4444'}).add_to(m)
        if show_ai:
             for ep in epicentros_ia:
                folium.Circle(location=[ep['lat'], ep['lon']], radius=1500, color="#EF4444", weight=1, fill=True, fill_opacity=0.1).add_to(m)
        st_folium(m, width="100%", height=500)
        render_forecast_section(sim_temp)

    with col_der:
        render_right_metrics(len(df))
        render_log_card(epicentros_ia)

elif pagina_actual == "Base":
    st.markdown("## Base de Datos Histórica")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif pagina_actual == "Analitica":
    st.markdown("## Analítica Volumétrica 3D")
    render_3d_density_map(df)

st.markdown('</div>', unsafe_allow_html=True)
render_footer()