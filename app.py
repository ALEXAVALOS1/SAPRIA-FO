import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SAPRIA-FO | NASA Link", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e: pass
local_css("assets/style.css")

# --- IMPORTS IMPORTANTES ---
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_nasa_firms_data
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_forecast_section, render_nasa_card
    # Ignoramos imports de simulación por si no los tienes aún para evitar errores
except ImportError as e:
    st.error(f"Faltan archivos: {e}")
    st.stop()

# --- VARIABLES ---
if 'page' not in st.session_state: st.session_state['page'] = 'Dashboard'
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 

# --- DATOS ---
@st.cache_data(ttl=600)
def get_data_bundle():
    df = load_historical_data("incendios.csv")
    weather = get_weather_data(JUAREZ_LAT, JUAREZ_LON)
    aqi = get_air_quality(JUAREZ_LAT, JUAREZ_LON)
    df_infra = get_real_infrastructure(JUAREZ_LAT, JUAREZ_LON, radius=10000)
    df_nasa = get_nasa_firms_data() # CONEXIÓN NASA!
    return df, weather, aqi, df_infra, df_nasa

df, weather, aqi, df_infra, df_nasa = get_data_bundle()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#E11D48; font-size:24px; margin:0;'>SAPRIA-FO</h1><p style='color:#3B82F6; font-weight:bold; font-size:11px;'>🚀 Space Command v5.0</p>", unsafe_allow_html=True)
    
    opcion = st.radio("Menú", ["🗺️ Monitor", "🔥 Incidentes", "⚠️ Riesgo", "📄 Reportes"], label_visibility="collapsed")
    if "Monitor" in opcion: st.session_state['page'] = 'Dashboard'
    else: st.session_state['page'] = 'Dashboard'

    st.markdown("---")
    if st.button("🚨 SIMULAR ALERTA", type="primary"):
        if hasattr(st, 'dialog'): 
            @st.dialog("ALERTA") 
            def m(): st.error("RIESGO DETECTADO"); st.button("OK", on_click=st.rerun)
            m()

# --- DASHBOARD PRINCIPAL ---
if st.session_state['page'] == 'Dashboard':
    render_top_navbar()
    col_main, col_sidebar = st.columns([3, 1])

    with col_main:
        # Mapa
        total = len(df) if not df.empty else 0
        st.markdown(render_map_floating_card(total, "Riberas del Bravo"), unsafe_allow_html=True)
        
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=11, tiles="CartoDB dark_matter")
        
        # Capa Histórica
        if not df.empty: HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#F59E0B', 1:'#E11D48'}).add_to(m)
        
        # Capa Infraestructura
        if not df_infra.empty:
            for _, r in df_infra.iterrows():
                ic = 'truck-medical' if r['tipo']=='Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], tooltip=r['nombre'], icon=folium.Icon(color="black", icon_color=r['color'], icon=ic, prefix="fa")).add_to(m)
        
        # 🛰️ CAPA SATELITAL NASA 🛰️
        if not df_nasa.empty:
            for _, r in df_nasa.iterrows():
                folium.CircleMarker(
                    location=[r['latitude'], r['longitude']],
                    radius=10, color="#EF4444", fill=True, fill_color="#EF4444", fill_opacity=0.7,
                    tooltip=f"ALERTA NASA: {r['bright_ti4']}K"
                ).add_to(m)
                folium.Marker([r['latitude'], r['longitude']], icon=folium.Icon(color="red", icon="satellite-dish", prefix="fa")).add_to(m)

        st_folium(m, width="100%", height=500)
        st.markdown(render_forecast_section(), unsafe_allow_html=True)

    with col_sidebar:
        # 🛰️ TARJETA NASA EN EL PANEL DERECHO
        st.markdown(render_nasa_card(df_nasa), unsafe_allow_html=True)
        
        st.markdown(render_risk_card("MODERADO", "Condiciones Estables"), unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        temp_val = f"{weather['main']['temp']}°" if weather else "--"
        hum_val = f"{weather['main']['humidity']}%" if weather else "--"
        with c1: st.markdown(render_small_stat("TEMP", temp_val, "fa-temperature-half", "#F59E0B", "rgba(245,158,11,0.1)"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUM", hum_val, "fa-droplet", "#3B82F6", "rgba(59,130,246,0.1)"), unsafe_allow_html=True)
        
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)

# Footer
st.markdown('<div class="mega-footer">© 2026 SAPRIA-FO • VIIRS Satellite Link Active 🛰️</div>', unsafe_allow_html=True)