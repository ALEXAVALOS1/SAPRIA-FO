import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap, AntPath
import pandas as pd
from datetime import datetime

# --- IMPORTACIONES ---
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_route_osrm, find_nearest_station
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_tactical_card, render_simulation_controls, render_impact_alert
    from src.report_generator import generate_pdf_report
    from src.simulation import get_fire_ellipse
    from src.fwi_calculator import calculate_fwi
    from src.geometry_utils import analyze_impact
    # NUEVO MÓDULO
    from src.analytics import render_3d_map, render_temporal_analysis, render_cause_analysis, render_kpi_metrics
except ImportError as e:
    st.error(f"Error crítico: {e}")
    st.stop()

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SAPRIA-FO | Intelligence", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
def local_css(file_name):
    with open(file_name, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("assets/style.css")

# --- VARIABLES ---
if 'page' not in st.session_state: st.session_state['page'] = 'Dashboard'
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
if 'manual_wind' not in st.session_state: st.session_state['manual_wind'] = 20

def set_page(p): st.session_state['page'] = p

# --- DATOS REALES ---
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 

@st.cache_data(ttl=600)
def get_data_bundle():
    df = load_historical_data("incendios.csv")
    weather = get_weather_data(JUAREZ_LAT, JUAREZ_LON)
    aqi = get_air_quality(JUAREZ_LAT, JUAREZ_LON)
    df_infra = get_real_infrastructure(JUAREZ_LAT, JUAREZ_LON, radius=10000)
    return df, weather, aqi, df_infra

df, weather, aqi, df_infra = get_data_bundle()

# --- INTERFAZ ---
render_top_navbar()

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h1 class="sidebar-title">SAPRIA-FO</h1><p class="sidebar-subtitle">Strategic Intelligence v8.0</p></div>', unsafe_allow_html=True)
    
    # Navegación
    pages = [("Comando", "fa-map-location-dot", "Dashboard"), ("Inteligencia", "fa-chart-pie", "Reportes")]
    for label, icon, pid in pages:
        active = "active" if st.session_state['page'] == pid else ""
        if st.button(f"⠀{label}", key=pid, use_container_width=True):
            set_page(pid)
            st.rerun()
        st.markdown(f'<div class="custom-nav-btn {active}" style="pointer-events:none; margin-top:-48px; position:relative; z-index:0;"><i class="fa-solid {icon}"></i> {label}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Panel Dinámico según página
    if st.session_state['page'] == 'Dashboard':
        st.markdown("### 🎮 SIMULADOR")
        sim_wind_speed = st.slider("Viento (km/h)", 0, 100, 35)
        sim_wind_deg = st.slider("Dirección (°)", 0, 360, 90)
        sim_temp = st.slider("Temp (°C)", -5, 50, 38)
        sim_hum = st.slider("Humedad (%)", 0, 100, 8)
        
        if st.button("Reiniciar Mapa"):
            st.session_state['sim_coords'] = None
            st.rerun()
    else:
        st.info("📊 Estás en el módulo de análisis histórico. Aquí puedes identificar patrones a largo plazo.")

# --- PÁGINA 1: DASHBOARD DE MANDO (IGUAL QUE ANTES) ---
if st.session_state['page'] == 'Dashboard':
    c_map, c_stats = st.columns([2.5, 1])
    
    # Cálculos Simulador
    fire_polygon = None
    impact_list = []
    fwi_val, fwi_cat, fwi_col = calculate_fwi(sim_temp, sim_hum, sim_wind_speed)

    if st.session_state['sim_coords']:
        sim_lat = st.session_state['sim_coords']['lat']
        sim_lon = st.session_state['sim_coords']['lng']
        fire_polygon = get_fire_ellipse(sim_lat, sim_lon, sim_wind_deg, sim_wind_speed)
        impact_list = analyze_impact(fire_polygon, df_infra)
    
    with c_map:
        total = len(df) if not df.empty else 0
        hotspot = df['colonia'].mode()[0] if not df.empty else "N/A"
        st.markdown(render_map_floating_card(total, hotspot), unsafe_allow_html=True)
        
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=12, tiles="CartoDB dark_matter")
        
        if not df.empty:
            HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4: '#F59E0B', 1: '#E11D48'}).add_to(m)
        
        if not df_infra.empty:
            for _, r in df_infra.iterrows():
                icon_name = 'truck-medical' if r['tipo'] == 'Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], popup=r['nombre'], icon=folium.Icon(color="black", icon_color=r['color'], icon=icon_name, prefix="fa")).add_to(m)
        
        if fire_polygon:
            folium.Polygon(locations=fire_polygon, color=fwi_col, weight=2, fill=True, fill_color=fwi_col, fill_opacity=0.4).add_to(m)
            folium.Marker([sim_lat, sim_lon], icon=folium.Icon(color="red", icon="fire", prefix="fa", spin=True)).add_to(m)
            for item in impact_list:
                folium.Marker([item['lat'], item['lon']], icon=folium.Icon(color="red", icon="triangle-exclamation", prefix="fa", spin=True)).add_to(m)

        map_data = st_folium(m, width="100%", height=550)
        if map_data['last_clicked']:
            if st.session_state['sim_coords'] != map_data['last_clicked']:
                st.session_state['sim_coords'] = map_data['last_clicked']
                st.rerun()

    with c_stats:
        if impact_list:
            st.markdown(render_impact_alert(impact_list), unsafe_allow_html=True)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        
        st.markdown(f"""<div class="dash-card" style="border-left: 4px solid {fwi_col};"><div style="font-size:10px; color:{fwi_col}; font-weight:bold;">SIMULACIÓN ACTIVA</div><div style="font-size:20px; color:white; font-weight:bold;">{fwi_cat} ({fwi_val:.1f})</div></div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: st.markdown(render_small_stat("TEMP", f"{weather['main']['temp']}°", "fa-temperature-half", "#F59E0B"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUMEDAD", f"{weather['main']['humidity']}%", "fa-droplet", "#3B82F6"), unsafe_allow_html=True)
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)

# --- PÁGINA 2: INTELIGENCIA DE DATOS (NUEVA) ---
elif st.session_state['page'] == 'Reportes':
    st.markdown("<h2 style='color:#E11D48;'>📡 DIVISIÓN DE INTELIGENCIA ESTRATÉGICA</h2>", unsafe_allow_html=True)
    
    # Métricas KPI
    render_kpi_metrics(df)
    st.markdown("---")
    
    # Fila 1: Mapa 3D y Causas
    c1, c2 = st.columns([2, 1])
    with c1:
        render_3d_map(df) # MAPA 3D CON PYDECK
    with c2:
        render_cause_analysis(df) # GRÁFICO SUNBURST
        
    st.markdown("---")
    
    # Fila 2: Análisis Temporal y Descarga
    c3, c4 = st.columns([2, 1])
    with c3:
        render_temporal_analysis(df) # MAPA DE CALOR TEMPORAL
    with c4:
        st.markdown("### 📄 EXPORTACIÓN OFICIAL")
        st.info("Generar expediente completo con gráficas, mapas y bitácora operativa.")
        if st.button("Generar Expediente PDF", use_container_width=True):
            pdf = generate_pdf_report(df, weather, aqi)
            st.download_button("📥 Descargar Expediente", pdf, "Expediente_Inteligencia.pdf", "application/pdf", use_container_width=True)

# Footer
st.markdown("""<div class="mega-footer"><div class="footer-bottom">© 2026 SAPRIA-FO • Intelligence Division</div></div>""", unsafe_allow_html=True)