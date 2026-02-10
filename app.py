import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap, AntPath
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="SAPRIA-FO", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# Cargar estilos CSS
def local_css(file_name):
    try:
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except: pass
local_css("assets/style.css")

# --- IMPORTS ---
try:
    from src.data_loader import load_historical_data, get_weather_data, get_real_infrastructure, get_air_quality, get_nasa_firms_data, find_nearest_station, get_route_osrm
    from src.components import render_top_navbar, render_risk_card, render_small_stat, render_map_floating_card, render_air_quality_card, render_forecast_section, render_nasa_card, render_tactical_card
    from src.fwi_calculator import calculate_fwi
    from src.ml_engine import get_risk_clusters, generate_ai_briefing
    from src.analytics import render_3d_density_map, render_statistics
    from src.report_generator import generate_pdf_report
except ImportError as e:
    st.error(f"Error crítico de importación: {e}")
    st.stop()

# --- GESTIÓN DE ESTADO ---
# Inicializamos la página en 'Monitor' si no existe
if 'page' not in st.session_state: st.session_state['page'] = 'Monitor'
if 'sim_coords' not in st.session_state: st.session_state['sim_coords'] = None
JUAREZ_LAT, JUAREZ_LON = 31.7389, -106.4856 

# --- CARGA DE DATOS ---
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

# ==============================================================================
# ÁREA PRINCIPAL SUPERIOR (BRANDING + NAVEGACIÓN HORIZONTAL)
# ==============================================================================

# 1. Barra Azul Oscura de Marca (HTML estático)
render_top_navbar()

# 2. Barra de Navegación Funcional (Radio Button Horizontal)
# El CSS se encarga de que parezcan pestañas/botones
nav_options = ["🗺️ Monitor Táctico", "📄 Reportes e Inteligencia", "🗃️ Base de Incidentes"]
selected_nav = st.radio("Navegación Principal", nav_options, horizontal=True, label_visibility="collapsed")

# Lógica de ruteo basada en la selección horizontal
if "Monitor" in selected_nav: st.session_state['page'] = 'Monitor'
elif "Reportes" in selected_nav: st.session_state['page'] = 'Reportes'
elif "Incidentes" in selected_nav: st.session_state['page'] = 'Incidentes'


# ==============================================================================
# SIDEBAR (BARRA LATERAL LIMPIA - SOLO FILTROS E INFO)
# ==============================================================================
with st.sidebar:
    # Ya no hay menú de navegación aquí. Solo herramientas.
    st.markdown("<div style='font-size:11px; font-weight:700; color:#FACC15; margin-bottom: 15px; letter-spacing:1px;'>HERRAMIENTAS TÁCTICAS</div>", unsafe_allow_html=True)
    
    # Botón de Alerta
    if st.button("🚨 ACTIVAR PROTOCOLO DE ALERTA", type="primary", use_container_width=True):
        if hasattr(st, 'dialog'):
            @st.dialog("CONFIRMAR ALERTA")
            def m(): st.warning("¿Desea emitir una alerta general?"); st.button("CONFIRMAR", type="primary", on_click=st.rerun)
            m()

    st.markdown("---")
    
    # Filtros de Capas
    st.markdown("<div style='font-size:11px; font-weight:700; color:#94A3B8; margin-bottom: 10px;'>VISUALIZACIÓN DE CAPAS</div>", unsafe_allow_html=True)
    show_heatmap = st.toggle("🔥 Mapa de Calor Histórico", value=True)
    show_ai = st.toggle("🧠 Zonas Predictivas IA", value=True)
    show_infra = st.toggle("🏭 Infraestructura Crítica", value=False)
    
    st.markdown("---")

    # Resumen de IA
    st.markdown("<div style='font-size:11px; font-weight:700; color:#94A3B8; margin-bottom: 10px;'>INTELIGENCIA ARTIFICIAL (K-MEANS)</div>", unsafe_allow_html=True)
    if epicentros_ia:
        for ep in epicentros_ia[:3]:
            col = "#EF4444" if ep['peligro'] == 'CRÍTICO' else "#F59E0B"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-top:8px; font-size:11px; border-left: 3px solid {col}; color:#F8FAFC;">
                <div style="font-weight:700;">Epicentro {ep["id"]}</div>
                <div style="color:#94A3B8;">Concentración: {ep["weight"]} eventos</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><div style='font-size:10px; color:#64748B; text-align:center;'>v9.5 Edición Corporativa</div>", unsafe_allow_html=True)


# ==============================================================================
# CUERPO PRINCIPAL (EL CONTENIDO CAMBIA SEGÚN LA NAVEGACIÓN SUPERIOR)
# ==============================================================================

# PANTALLA 1: MONITOR
if st.session_state['page'] == 'Monitor':
    col_main, col_sidebar = st.columns([2.8, 1.2]) # Distribución 70% / 30%
    route_data, nearest_station = None, None

    with col_main:
        st.markdown(generate_ai_briefing(weather, fwi_cat, len(df_nasa), epicentros_ia), unsafe_allow_html=True)
        st.markdown(render_map_floating_card(len(df) if not df.empty else 0, "Riberas del Bravo"), unsafe_allow_html=True)
        
        # Mapa Claro (Positron)
        m = folium.Map(location=[JUAREZ_LAT, JUAREZ_LON], zoom_start=11, tiles="CartoDB positron")
        
        # Capas Condicionales
        if show_heatmap and not df.empty: HeatMap([[r['lat'], r['lon']] for _, r in df.iterrows()], radius=15, gradient={0.4:'#F59E0B', 1:'#E11D48'}).add_to(m)
        if show_infra and not df_infra.empty:
            for _, r in df_infra.iterrows():
                ic = 'truck-medical' if r['tipo']=='Bomberos' else r['icon']
                folium.Marker([r['lat'], r['lon']], tooltip=r['nombre'], icon=folium.Icon(color="lightgray", icon_color=r['color'], icon=ic, prefix="fa")).add_to(m)
        if not df_nasa.empty: # NASA siempre visible
            for _, r in df_nasa.iterrows():
                folium.CircleMarker(location=[r['latitude'], r['longitude']], radius=10, color="#EF4444", fill=True, fill_color="#EF4444", fill_opacity=0.7).add_to(m)
                folium.Marker([r['latitude'], r['longitude']], icon=folium.Icon(color="red", icon="satellite-dish", prefix="fa")).add_to(m)
        if show_ai:
            for ep in epicentros_ia:
                color_zona = "#E11D48" if ep['peligro'] == "CRÍTICO" else "#F59E0B"
                folium.Circle(location=[ep['lat'], ep['lon']], radius=1500, color=color_zona, weight=1, fill=True, fill_opacity=0.1).add_to(m)

        # Lógica de Ruteo al Clic
        if st.session_state['sim_coords']:
            sim_lat, sim_lon = st.session_state['sim_coords']['lat'], st.session_state['sim_coords']['lng']
            folium.Marker([sim_lat, sim_lon], icon=folium.Icon(color="red", icon="fire", prefix="fa")).add_to(m)
            nearest_station = find_nearest_station(sim_lat, sim_lon, df_infra)
            if nearest_station is not None:
                folium.Marker([nearest_station['lat'], nearest_station['lon']], tooltip=f"ORIGEN: {nearest_station['nombre']}", icon=folium.Icon(color="blue", icon="truck-medical", prefix="fa")).add_to(m)
                route_data = get_route_osrm(nearest_station['lat'], nearest_station['lon'], sim_lat, sim_lon)
                if route_data: AntPath(locations=route_data['path'], color="#3B82F6", weight=5, opacity=0.8, delay=800, dash_array=[10, 20]).add_to(m)

        map_data = st_folium(m, width="100%", height=450)
        if map_data['last_clicked'] and st.session_state['sim_coords'] != map_data['last_clicked']:
            st.session_state['sim_coords'] = map_data['last_clicked']; st.rerun()
            
        st.markdown(render_forecast_section(), unsafe_allow_html=True)

    with col_sidebar:
        if route_data and nearest_station is not None: st.markdown(render_tactical_card(route_data, nearest_station['nombre']), unsafe_allow_html=True)
        st.markdown(render_risk_card(fwi_cat, "Condiciones estables."), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(render_small_stat("TEMP", f"{sim_temp}°", "fa-temperature-half", "#FACC15"), unsafe_allow_html=True)
        with c2: st.markdown(render_small_stat("HUMEDAD", f"{sim_hum}%", "fa-droplet", "#3B82F6"), unsafe_allow_html=True)
        st.markdown(render_nasa_card(df_nasa), unsafe_allow_html=True)
        st.markdown(render_air_quality_card(aqi), unsafe_allow_html=True)

# PANTALLA 2: REPORTES
elif st.session_state['page'] == 'Reportes':
    st.markdown("<h2 style='color:#0F172A; font-weight:800;'>División de Inteligencia Estratégica</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B;'>Análisis avanzado y generación de documentación oficial.</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    col_pdf, col_empty = st.columns([1, 2])
    with col_pdf:
        st.markdown("<h4 style='color:#0F172A; margin-bottom:10px;'><i class='fa-solid fa-file-pdf' style='color:#E11D48;'></i> Informes Tácticos</h4>", unsafe_allow_html=True)
        if st.button("📄 GENERAR PDF OFICIAL", type="primary", use_container_width=True):
            with st.spinner("Compilando datos..."):
                try:
                    pdf_path = generate_pdf_report(weather, fwi_cat, len(df_nasa), epicentros_ia)
                    with open(pdf_path, "rb") as f:
                        st.download_button("⬇️ DESCARGAR DOCUMENTO", data=f, file_name=f"SAPRIA_Reporte_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e: st.error(f"Error PDF: {e}")

    st.markdown("<hr style='margin-top:30px;'>", unsafe_allow_html=True)
    render_3d_density_map(df)
    render_statistics(df)

# PANTALLA 3: INCIDENTES
elif st.session_state['page'] == 'Incidentes':
    st.markdown("<h2 style='color:#0F172A; font-weight:800;'>Base de Datos Operativa</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df[['fecha', 'colonia', 'tipo_incidente', 'causa', 'dano']], use_container_width=True, height=600)
    else:
        st.info("Sin datos disponibles.")

# FOOTER CORPORATIVO
st.markdown("""
<div class="mega-footer">
    <div style="display:flex; justify-content:space-around; max-width:1200px; margin:0 auto; align-items:flex-start;">
        <div><h2 style="margin:0; font-size:22px;">SAPRIA-FO</h2><p>Inteligencia Municipal</p></div>
        <div><h4>SOPORTE</h4><p>Mesa de Ayuda<br>Documentación<br>Estado del Sistema</p></div>
        <div><h4>CONTACTO</h4><p>Emergencias: 911<br>Centro de Mando Juárez</p></div>
    </div>
    <div style="text-align:center; margin-top:30px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.1); font-size:11px;">
        © 2026 Gobierno Municipal de Juárez. Todos los derechos reservados.
    </div>
</div>
""", unsafe_allow_html=True)