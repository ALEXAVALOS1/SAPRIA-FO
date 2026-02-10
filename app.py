import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap, AntPath
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SAPRIA-FO | Multi-Screen", page_icon="🖥️", layout="wide", initial_sidebar_state="expanded")

def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e: pass
local_css("assets/style.css")

# --- IMPORTS LOCALES ---
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_nasa_firms_data, find_nearest_station, get_route_osrm
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_forecast_section, render_nasa_card, render_tactical_card
    from src.fwi_calculator import calculate_fwi
    from src.ml_engine import get_risk_clusters, generate_ai_briefing
    from src.analytics import render_3d_density_map, render_statistics
    from src.report_generator import generate_pdf_report
except ImportError as e:
    st.error(f"Error cargando módulos: {e}")
    st.stop()

# --- VARIABLES GLOBALES ---
if 'page' not in st.session_state: st.session_state['page'] = 'Monitor'
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
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
epicentros_ia = get_risk_clusters(df, num_clusters=5)

sim_wind_speed = weather['wind']['speed'] * 3.6 if weather else 20
sim_temp = weather['main']['temp'] if weather else 30
sim_hum = weather['main']['humidity'] if weather else 20
fwi_val, fwi_cat, fwi_col = calculate_fwi(sim_temp, sim_hum, sim_wind_speed)

# --- SIDEBAR & NAVEGACIÓN ---
with st.sidebar:
    st.markdown("<h1 style='color:#E11D48; font-size:24px; margin:0;'>SAPRIA-FO</h1><p style='color:#10B981; font-weight:bold; font-size:11px;'>🌐 Global Intel v8.5</p>", unsafe_allow_html=True)
    opcion = st.radio("Menú", ["🗺️ Monitor", "🔥 Incidentes", "📄 Reportes"], label_visibility="collapsed")
    if "Monitor" in opcion: st.session_state['page'] = 'Monitor'
    elif "Incidentes" in opcion: st.session_state['page'] = 'Incidentes'
    elif "Reportes" in opcion: st.session_state['page'] = 'Reportes'

    st.markdown("---")
    
    # --- FILTROS TÁCTICOS (NUEVO) ---
    st.markdown("<div style='font-size:10px; color:#64748B; margin-bottom: 10px;'>FILTROS DE CAPAS</div>", unsafe_allow_html=True)
    show_heatmap = st.toggle("🔥 Mapa de Calor", value=True)
    show_ai = st.toggle("🧠 Zonas Predictivas IA", value=True)
    show_infra = st.toggle("🏭 Infraestructura Crítica", value=False) # ¡Apagado por defecto para limpiar el mapa!
    
    st.markdown("---")
    st.markdown("<div style='font-size:10px; color:#64748B;'>CLÚSTERES IA (K-MEANS)</div>", unsafe_allow_html=True)
    if epicentros_ia:
        for ep in epicentros_ia[:3]:
            col = "#EF4444" if ep['peligro'] == 'CRÍTICO' else "#F59E0B"
            st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:8px; border-radius:6px; margin-top:5px; font-size:11px; border-left: 2px solid {col};"><b style="color:white;">Epicentro {ep["id"]}</b><br><span style="color:#94A3B8;">Concentración: {ep["weight"]} eventos</span></div>', unsafe_allow_html=True)

render_top_navbar()

# ==========================================
# PANTALLA 1: MONITOR (DASHBOARD TÁCTICO)
# ==========================================
if st.session_state['page'] == 'Monitor':
    col_main, col_sidebar = st.columns([3, 1])

    route_data = None
    nearest_station = None

    with col_main:
        num_anomalias = len(df_nasa) if not df_nasa.empty else 0
        st.markdown(generate_ai_briefing(weather, fwi_cat, num_anomalias, epicentros_ia), unsafe_allow_html=True)
        total = len(df) if not df.empty else 0
        st.markdown(render_map_floating_card(total, "Riberas del Bravo"), unsafe_allow_html=True)
        
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=11, tiles="CartoDB dark_matter")
        
        # 1. Capa Histórica (Condicional)
        if show_heatmap and not df.empty: 
            HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#F59E0B', 1:'#E11D48'}).add_to(m)
        
        # 2. Capa Infraestructura (Condicional)
        if show_infra and not df_infra.empty:
            for _, r in df_infra.iterrows():
                ic = 'truck-medical' if r['tipo']=='Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], tooltip=r['nombre'], icon=folium.Icon(color="black", icon_color=r['color'], icon=ic, prefix="fa")).add_to(m)
        
        # 3. Capa NASA (Siempre visible por seguridad)
        if not df_nasa.empty:
            for _, r in df_nasa.iterrows():
                folium.CircleMarker(location=[r['latitude'], r['longitude']], radius=10, color="#EF4444", fill=True, fill_color="#EF4444", fill_opacity=0.7).add_to(m)
                folium.Marker([r['latitude'], r['longitude']], icon=folium.Icon(color="red", icon="satellite-dish", prefix="fa")).add_to(m)
        
        # 4. Capa IA (Condicional)
        if show_ai:
            for ep in epicentros_ia:
                color_zona = "#E11D48" if ep['peligro'] == "CRÍTICO" else "#F59E0B"
                folium.Circle(location=[ep['lat'], ep['lon']], radius=1500, color=color_zona, weight=1, fill=True, fill_opacity=0.1).add_to(m)
                folium.Marker([ep['lat'], ep['lon']], icon=folium.Icon(color="purple" if ep['peligro']=="CRÍTICO" else "orange", icon="brain", prefix="fa")).add_to(m)

        # 5. Ruteo (Animación al hacer clic)
        if st.session_state['sim_coords']:
            sim_lat = st.session_state['sim_coords']['lat']
            sim_lon = st.session_state['sim_coords']['lng']
            folium.Marker([sim_lat, sim_lon], icon=folium.Icon(color="red", icon="fire", prefix="fa")).add_to(m)
            
            nearest_station = find_nearest_station(sim_lat, sim_lon, df_infra)
            if nearest_station is not None:
                # Asegurarnos de dibujar la estación origen aunque la capa esté oculta
                folium.Marker([nearest_station['lat'], nearest_station['lon']], tooltip=f"ORIGEN: {nearest_station['nombre']}", icon=folium.Icon(color="blue", icon="truck-medical", prefix="fa")).add_to(m)
                route_data = get_route_osrm(nearest_station['lat'], nearest_station['lon'], sim_lat, sim_lon)
                if route_data:
                    AntPath(locations=route_data['path'], color="#3B82F6", weight=5, opacity=0.8, delay=800, dash_array=[10, 20]).add_to(m)

        map_data = st_folium(m, width="100%", height=480)
        
        if map_data['last_clicked'] and st.session_state['sim_coords'] != map_data['last_clicked']:
            st.session_state['sim_coords'] = map_data['last_clicked']
            st.rerun()
            
        st.markdown(render_forecast_section(), unsafe_allow_html=True)

    with col_sidebar:
        if route_data and nearest_station is not None:
            st.markdown(render_tactical_card(route_data, nearest_station['nombre']), unsafe_allow_html=True)
            
        st.markdown(render_nasa_card(df_nasa), unsafe_allow_html=True)
        st.markdown(render_risk_card(fwi_cat, "Basado en clima real"), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(render_small_stat("TEMP", f"{sim_temp}°", "fa-temperature-half", "#F59E0B", "rgba(245,158,11,0.1)"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUM", f"{sim_hum}%", "fa-droplet", "#3B82F6", "rgba(59,130,246,0.1)"), unsafe_allow_html=True)
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)

# ==========================================
# PANTALLA 2 Y 3: REPORTES E INCIDENTES
# ==========================================
elif st.session_state['page'] == 'Reportes':
    st.markdown("<h2 style='color:#E11D48;'>División de Inteligencia Estratégica</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Panel de análisis avanzado.</p><hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#F8FAFC;'><i class='fa-solid fa-file-pdf' style='color:#E11D48;'></i> Generador de Informes Tácticos</h3>", unsafe_allow_html=True)
    if st.button("📄 GENERAR INFORME OFICIAL (PDF)", type="primary"):
        with st.spinner("Compilando datos..."):
            try:
                num_anomalias = len(df_nasa) if not df_nasa.empty else 0
                pdf_path = generate_pdf_report(weather, fwi_cat, num_anomalias, epicentros_ia)
                with open(pdf_path, "rb") as f:
                    st.download_button(label="⬇️ DESCARGAR DOCUMENTO", data=f, file_name=f"SAPRIA_Reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
                st.success("¡Informe generado!")
            except Exception as e:
                st.error(f"Error PDF: {e}")
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    render_3d_density_map(df)
    render_statistics(df)

elif st.session_state['page'] == 'Incidentes':
    st.markdown("<h2 style='color:#F59E0B;'>Base de Datos Operativa</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df[['fecha', 'colonia', 'tipo_incidente', 'causa', 'dano']], use_container_width=True, height=500)

st.markdown('<div class="mega-footer">© 2026 SAPRIA-FO • Global Intelligence Multi-Screen System 🌐</div>', unsafe_allow_html=True)