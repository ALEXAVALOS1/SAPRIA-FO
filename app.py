import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap, AntPath
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SAPRIA-FO", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# Carga segura de CSS (Arregla error Unicode)
def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Error CSS: {e}")

local_css("assets/style.css")

# Imports con manejo de errores (Evita pantalla roja)
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_route_osrm, find_nearest_station
    # Importamos TODO
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_tactical_card, render_simulation_controls, render_impact_alert, render_forecast_section
    from src.report_generator import generate_pdf_report
    from src.simulation import get_fire_ellipse
    from src.fwi_calculator import calculate_fwi
    from src.geometry_utils import analyze_impact
except ImportError as e:
    st.error(f"⚠️ Faltan archivos: {e}. Revisa src/components.py")
    st.stop()

# --- VARIABLES ---
if 'page' not in st.session_state: st.session_state['page'] = 'Dashboard'
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
if 'manual_wind' not in st.session_state: st.session_state['manual_wind'] = 20
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 

# --- DATOS ---
@st.cache_data(ttl=600)
def get_data_bundle():
    df = load_historical_data("incendios.csv")
    weather = get_weather_data(JUAREZ_LAT, JUAREZ_LON)
    aqi = get_air_quality(JUAREZ_LAT, JUAREZ_LON)
    df_infra = get_real_infrastructure(JUAREZ_LAT, JUAREZ_LON, radius=10000)
    return df, weather, aqi, df_infra
df, weather, aqi, df_infra = get_data_bundle()

# --- SIDEBAR MEJORADO ---
with st.sidebar:
    st.markdown("<h1 style='color:#E11D48; font-size:24px; margin:0;'>SAPRIA-FO</h1><p style='color:#94A3B8; font-size:11px;'>Centro de Comando v4.6</p>", unsafe_allow_html=True)
    
    # MENÚ ARREGLADO (st.radio + CSS es mucho más estable)
    opcion = st.radio("Menú", ["🗺️ Monitor", "🔥 Incidentes", "⚠️ Riesgo", "📈 Predicción", "📄 Reportes"], label_visibility="collapsed")
    
    if "Monitor" in opcion: st.session_state['page'] = 'Dashboard'
    elif "Reportes" in opcion: st.session_state['page'] = 'Reportes'
    else: st.session_state['page'] = 'Dashboard'

    st.markdown("---")
    
    # DIALOG ARREGLADO (Detecta versión)
    if st.button("🚨 SIMULAR ALERTA", type="primary"):
        if hasattr(st, 'dialog'): 
            @st.dialog("ALERTA") 
            def m(): st.error("RIESGO DETECTADO"); st.write("Evacuar zona."); st.button("OK", on_click=st.rerun)
            m()
        elif hasattr(st, 'experimental_dialog'):
            @st.experimental_dialog("ALERTA")
            def m(): st.error("RIESGO DETECTADO"); st.write("Evacuar zona."); st.button("OK", on_click=st.rerun)
            m()
        else:
            st.sidebar.error("¡ALERTA!")

# --- DASHBOARD ---
if st.session_state['page'] == 'Dashboard':
    render_top_navbar()
    col_main, col_sidebar = st.columns([3, 1])

    with col_main:
        # Mapa
        total = len(df) if not df.empty else 0
        hotspot = df['colonia'].mode()[0] if not df.empty else "N/A"
        st.markdown(render_map_floating_card(total, hotspot), unsafe_allow_html=True)
        
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=12, tiles="CartoDB dark_matter")
        if not df.empty: HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#F59E0B', 1:'#E11D48'}).add_to(m)
        if not df_infra.empty:
            for _, r in df_infra.iterrows():
                icon_c = 'truck-medical' if r['tipo']=='Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], popup=r['nombre'], icon=folium.Icon(color="black", icon_color=r['color'], icon=icon_c, prefix="fa")).add_to(m)
        
        st_folium(m, width="100%", height=500)
        
        # PRONÓSTICO (AQUÍ ESTABA EL ERROR DEL HTML BLANCO)
        # Agregamos unsafe_allow_html=True para que se vea el diseño y no el código
        st.markdown(render_forecast_section(), unsafe_allow_html=True)

    with col_sidebar:
        st.markdown(render_risk_card("MODERADO", "Condiciones Estables"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        temp_val = f"{weather['main']['temp']}°" if weather else "--"
        hum_val = f"{weather['main']['humidity']}%" if weather else "--"
        with c1: st.markdown(render_small_stat("TEMP", temp_val, "fa-temperature-half", "#F59E0B", "rgba(245,158,11,0.1)"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUM", hum_val, "fa-droplet", "#3B82F6", "rgba(59,130,246,0.1)"), unsafe_allow_html=True)
        
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)
        
        st.markdown("### Bitácora")
        if not df.empty:
            for i, r in df.head(3).iterrows():
                st.markdown(f"""<div class="log-item"><div class="log-title">{r['colonia']}</div><div class="log-sub">{r['tipo_incidente']} • {r['fecha'].strftime('%Y-%m-%d')}</div></div>""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="mega-footer">© 2026 SAPRIA-FO • Sistema de Inteligencia Municipal</div>', unsafe_allow_html=True)