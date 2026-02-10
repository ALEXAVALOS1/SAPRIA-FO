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

# Imports
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_nasa_firms_data
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_forecast_section, render_simulation_controls, render_impact_alert, render_tactical_card, render_nasa_card
    from src.simulation import get_fire_ellipse
    from src.fwi_calculator import calculate_fwi
    from src.geometry_utils import analyze_impact
except ImportError as e:
    st.error(f"Faltan archivos: {e}")
    st.stop()

# --- VARIABLES ---
if 'page' not in st.session_state: st.session_state['page'] = 'Dashboard'
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 

# --- DATOS (Agregamos la NASA) ---
@st.cache_data(ttl=600)
def get_data_bundle():
    df = load_historical_data("incendios.csv")
    weather = get_weather_data(JUAREZ_LAT, JUAREZ_LON)
    aqi = get_air_quality(JUAREZ_LAT, JUAREZ_LON)
    df_infra = get_real_infrastructure(JUAREZ_LAT, JUAREZ_LON, radius=10000)
    df_nasa = get_nasa_firms_data() # <--- ENLACE SATELITAL
    return df, weather, aqi, df_infra, df_nasa
df, weather, aqi, df_infra, df_nasa = get_data_bundle()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#E11D48; font-size:24px; margin:0;'>SAPRIA-FO</h1><p style='color:#94A3B8; font-size:11px;'>Space Command v5.0</p>", unsafe_allow_html=True)
    opcion = st.radio("Menú", ["🗺️ Monitor", "🔥 Incidentes", "⚠️ Riesgo", "📄 Reportes"], label_visibility="collapsed")
    
    if "Monitor" in opcion: st.session_state['page'] = 'Dashboard'
    else: st.session_state['page'] = 'Dashboard'
    st.markdown("---")
    
    # MODO SIMULACIÓN MANUAL
    st.markdown("<div style='font-size:11px; color:#64748B; margin-bottom:10px;'>PARÁMETROS DE SIMULACIÓN</div>", unsafe_allow_html=True)
    sim_wind_speed = st.slider("Viento (km/h)", 0, 100, 25)
    sim_wind_deg = st.slider("Dirección (°)", 0, 360, 45)

# --- DASHBOARD ---
if st.session_state['page'] == 'Dashboard':
    render_top_navbar()
    col_main, col_sidebar = st.columns([3, 1])

    # Lógica de FWI
    sim_temp = weather['main']['temp'] if weather else 30
    sim_hum = weather['main']['humidity'] if weather else 20
    fwi_val, fwi_cat, fwi_col = calculate_fwi(sim_temp, sim_hum, sim_wind_speed)

    with col_main:
        total = len(df) if not df.empty else 0
        hotspot = df['colonia'].mode()[0] if not df.empty else "N/A"
        st.markdown(render_map_floating_card(total, hotspot), unsafe_allow_html=True)
        
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=11, tiles="CartoDB dark_matter")
        
        # Capas Base
        if not df.empty: HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#F59E0B', 1:'#E11D48'}).add_to(m)
        if not df_infra.empty:
            for _, r in df_infra.iterrows():
                icon_c = 'truck-medical' if r['tipo']=='Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], tooltip=r['nombre'], icon=folium.Icon(color="black", icon_color=r['color'], icon=icon_c, prefix="fa")).add_to(m)
        
        # 🛰️ CAPA SATELITAL NASA 🛰️
        if not df_nasa.empty:
            for _, r in df_nasa.iterrows():
                # Dibujamos un radar parpadeante donde el satélite vio fuego
                folium.CircleMarker(
                    location=[r['latitude'], r['longitude']],
                    radius=8, color="#EF4444", fill=True, fill_color="#EF4444", fill_opacity=0.7,
                    tooltip=f"¡ALERTA NASA! Brillo: {r['bright_ti4']}K"
                ).add_to(m)
                folium.Marker(
                    [r['latitude'], r['longitude']], 
                    icon=folium.Icon(color="red", icon="satellite-dish", prefix="fa")
                ).add_to(m)

        # Simulación (Clic)
        if st.session_state['sim_coords']:
            sim_lat, sim_lon = st.session_state['sim_coords']['lat'], st.session_state['sim_coords']['lng']
            fire_poly = get_fire_ellipse(sim_lat, sim_lon, sim_wind_deg, sim_wind_speed)
            impact_list = analyze_impact(fire_poly, df_infra)
            
            folium.Polygon(locations=fire_poly, color=fwi_col, weight=2, fill=True, fill_color=fwi_col, fill_opacity=0.4).add_to(m)
            folium.Marker([sim_lat, sim_lon], icon=folium.Icon(color="red", icon="fire", prefix="fa", spin=True)).add_to(m)
            for item in impact_list: folium.Marker([item['lat'], item['lon']], icon=folium.Icon(color="red", icon="triangle-exclamation", prefix="fa")).add_to(m)

        map_data = st_folium(m, width="100%", height=550)
        if map_data['last_clicked'] and st.session_state['sim_coords'] != map_data['last_clicked']:
            st.session_state['sim_coords'] = map_data['last_clicked']; st.rerun()
            
        st.markdown(render_forecast_section(), unsafe_allow_html=True)

    with col_sidebar:
        # 🛰️ TARJETA NASA (¡NUEVA!)
        st.markdown(render_nasa_card(df_nasa), unsafe_allow_html=True)
        
        # Riesgo y Clima
        st.markdown(render_risk_card(fwi_cat, "Basado en viento/clima actual"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        temp_val = f"{weather['main']['temp']}°" if weather else "--"
        hum_val = f"{weather['main']['humidity']}%" if weather else "--"
        with c1: st.markdown(render_small_stat("TEMP", temp_val, "fa-temperature-half", "#F59E0B", "rgba(245,158,11,0.1)"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUM", hum_val, "fa-droplet", "#3B82F6", "rgba(59,130,246,0.1)"), unsafe_allow_html=True)
        
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)

# Footer
st.markdown('<div class="mega-footer">© 2026 SAPRIA-FO • VIIRS Satellite Tracking Active</div>', unsafe_allow_html=True)