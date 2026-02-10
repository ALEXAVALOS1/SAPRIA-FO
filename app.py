import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SAPRIA-FO | AI Command", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e: pass
local_css("assets/style.css")

# --- IMPORTS ---
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_nasa_firms_data
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_forecast_section, render_nasa_card
    from src.fwi_calculator import calculate_fwi
    # CONEXIÓN AL CEREBRO DE IA (JARVIS)
    from src.ml_engine import get_risk_clusters, generate_ai_briefing
except ImportError as e:
    st.error(f"Error cargando módulos: {e}")
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
    df_nasa = get_nasa_firms_data()
    return df, weather, aqi, df_infra, df_nasa

df, weather, aqi, df_infra, df_nasa = get_data_bundle()

# --- ENTRENAMIENTO DE IA EN VIVO ---
epicentros_ia = get_risk_clusters(df, num_clusters=5)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#E11D48; font-size:24px; margin:0;'>SAPRIA-FO</h1><p style='color:#8B5CF6; font-weight:bold; font-size:11px;'>🧠 AI Predictor v6.0</p>", unsafe_allow_html=True)
    
    opcion = st.radio("Menú", ["🗺️ Monitor", "🔥 Incidentes", "⚠️ Riesgo", "📄 Reportes"], label_visibility="collapsed")
    if "Monitor" in opcion: st.session_state['page'] = 'Dashboard'
    else: st.session_state['page'] = 'Dashboard'

    st.markdown("---")
    
    # Mostrar resumen de los epicentros IA en el menú
    st.markdown("<div style='font-size:10px; color:#64748B;'>CLÚSTERES IA (K-MEANS)</div>", unsafe_allow_html=True)
    if epicentros_ia:
        for ep in epicentros_ia[:3]: # Muestra los 3 más peligrosos
            col = "#EF4444" if ep['peligro'] == 'CRÍTICO' else "#F59E0B"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); padding:8px; border-radius:6px; margin-top:5px; font-size:11px; border-left: 2px solid {col};">
                <b style="color:white;">Epicentro {ep['id']}</b><br>
                <span style="color:#94A3B8;">Concentración: {ep['weight']} eventos</span>
            </div>
            """, unsafe_allow_html=True)

# --- DASHBOARD PRINCIPAL ---
if st.session_state['page'] == 'Dashboard':
    render_top_navbar()
    col_main, col_sidebar = st.columns([3, 1])

    # Lógica base
    sim_wind_speed = weather['wind']['speed'] * 3.6 if weather else 20
    sim_temp = weather['main']['temp'] if weather else 30
    sim_hum = weather['main']['humidity'] if weather else 20
    fwi_val, fwi_cat, fwi_col = calculate_fwi(sim_temp, sim_hum, sim_wind_speed)

    with col_main:
        # 🤖 AQUÍ APARECE JARVIS (AUTO-BRIEFING DE LA IA) 🤖
        num_anomalias = len(df_nasa) if not df_nasa.empty else 0
        st.markdown(generate_ai_briefing(weather, fwi_cat, num_anomalias, epicentros_ia), unsafe_allow_html=True)
        
        # Mapa Base
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
        
        # Capa Satelital NASA
        if not df_nasa.empty:
            for _, r in df_nasa.iterrows():
                folium.CircleMarker(location=[r['latitude'], r['longitude']], radius=10, color="#EF4444", fill=True, fill_color="#EF4444", fill_opacity=0.7).add_to(m)
                folium.Marker([r['latitude'], r['longitude']], icon=folium.Icon(color="red", icon="satellite-dish", prefix="fa")).add_to(m)

        # 🧠 CAPA DE EPICENTROS PREDICTIVOS DE LA IA 🧠
        for ep in epicentros_ia:
            color_zona = "#E11D48" if ep['peligro'] == "CRÍTICO" else "#F59E0B"
            # Círculo de Peligro Predictivo
            folium.Circle(
                location=[ep['lat'], ep['lon']], radius=1500, color=color_zona, weight=1, fill=True, fill_opacity=0.1,
                tooltip=f"IA Epicentro {ep['id']}: Alto Riesgo Predictivo"
            ).add_to(m)
            # Marcador de Cerebro
            folium.Marker(
                [ep['lat'], ep['lon']], 
                icon=folium.Icon(color="purple" if ep['peligro']=="CRÍTICO" else "orange", icon="brain", prefix="fa")
            ).add_to(m)

        st_folium(m, width="100%", height=480)
        st.markdown(render_forecast_section(), unsafe_allow_html=True)

    with col_sidebar:
        st.markdown(render_nasa_card(df_nasa), unsafe_allow_html=True)
        st.markdown(render_risk_card(fwi_cat, "Basado en clima real"), unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: st.markdown(render_small_stat("TEMP", f"{sim_temp}°", "fa-temperature-half", "#F59E0B", "rgba(245,158,11,0.1)"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUM", f"{sim_hum}%", "fa-droplet", "#3B82F6", "rgba(59,130,246,0.1)"), unsafe_allow_html=True)
        
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)

# Footer
st.markdown('<div class="mega-footer">© 2026 SAPRIA-FO • K-Means AI Engine Active 🧠</div>', unsafe_allow_html=True)