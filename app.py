import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
from datetime import datetime

# --- 1. IMPORTACIÓN DE MÓDULOS ---
try:
    from src.data_loader import load_historical_data, get_weather_data
    from src.ai_model import train_fire_model, predict_risk_grid
except ImportError as e:
    st.error(f"❌ Error: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="SAPRIA-FO | Monitoreo", page_icon="🔥", layout="wide")

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: pass

local_css("assets/style.css")

# --- 3. DATOS ---
df_incendios = load_historical_data("incendios.csv")
JUAREZ_COORDS = [31.6904, -106.4245]

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("SAPRIA-FO")
    st.markdown("---")
    opcion_menu = st.radio("Menú", ["📡 Monitoreo en Vivo", "🤖 Predicción IA"])
    
    # Filtros
    filtro_colonia = "Todas"
    if not df_incendios.empty:
        st.markdown("---")
        colonias = ["Todas"] + sorted(df_incendios['colonia'].dropna().unique().tolist())
        filtro_colonia = st.selectbox("Filtrar Zona:", colonias)

# --- 5. INTERFAZ PRINCIPAL ---
c1, c2 = st.columns([3, 1])
with c1: st.markdown("## SAPRIA-FO: Sistema de Análisis Predictivo")
with c2: st.markdown(f"**{datetime.now().strftime('%d/%m/%Y %H:%M')}**")

col_map, col_stats = st.columns([3, 1])

with col_map:
    # --- CONFIGURACIÓN DE MAPA LIMPIO ---
    m = folium.Map(location=JUAREZ_COORDS, zoom_start=12, tiles=None)

    # Capas Base
    folium.TileLayer("CartoDB dark_matter", name="Modo Oscuro (Base)", show=True).add_to(m)
    folium.TileLayer("OpenStreetMap", name="Callejero (Claro)", show=False).add_to(m)

    # Filtrar datos
    df_view = df_incendios.copy()
    if filtro_colonia != "Todas" and not df_incendios.empty:
        df_view = df_view[df_view['colonia'] == filtro_colonia]
        if not df_view.empty:
            m.location = [df_view.iloc[0]['lat'], df_view.iloc[0]['lon']]
            m.zoom_start = 14

    # --- LÓGICA DE CAPAS ---
    if opcion_menu == "📡 Monitoreo en Vivo" and not df_view.empty:
        # 1. Mapa de Calor (SOLO SI SE ACTIVA) - AHORA ES NÍTIDO
        # Ajuste: blur=6 (muy bajo) para quitar efecto neblina
        heat_data = [[row['lat'], row['lon']] for index, row in df_view.iterrows()]
        HeatMap(
            heat_data,
            radius=10, 
            blur=6,          # <--- AQUÍ ESTÁ EL TRUCO (Adiós neblina)
            min_opacity=0.4,
            gradient={0.4: 'cyan', 0.6: 'lime', 1: 'red'},
            name="🔥 Mapa de Calor (On/Off)"
        ).add_to(m)

        # 2. Puntos Exactos (Siempre visibles y limpios)
        marker_cluster = MarkerCluster(name="📍 Puntos de Incendio").add_to(m)
        for index, row in df_view.iterrows():
            folium.Marker(
                [row['lat'], row['lon']],
                popup=f"{row['colonia']} - {row['tipo_incidente']}",
                icon=folium.Icon(color="red", icon="fire", prefix="fa")
            ).add_to(marker_cluster)

    elif opcion_menu == "🤖 Predicción IA" and not df_incendios.empty:
        with st.spinner("Calculando riesgos..."):
            model, acc = train_fire_model(df_incendios)
            st.success(f"Precisión del Modelo: {acc:.1%}")
            
            # Grid de predicción
            grid = predict_risk_grid(model, df_incendios['lat'].min(), df_incendios['lat'].max(), 
                                   df_incendios['lon'].min(), df_incendios['lon'].max(), datetime.now())
            high_risk = grid[grid['risk_prob'] > 0.5]
            
            if not high_risk.empty:
                HeatMap(
                    [[r['lat'], r['lon'], r['risk_prob']] for i, r in high_risk.iterrows()],
                    radius=15, blur=10, gradient={0.5: 'orange', 1: 'red'},
                    name="⚠️ Zonas de Riesgo IA"
                ).add_to(m)

    # CONTROL DE CAPAS (Para que puedas apagar lo que no te guste)
    folium.LayerControl(collapsed=False).add_to(m)
    st_data = st_folium(m, width="100%", height=550)

with col_stats:
    st.markdown("### 📊 Métricas")
    weather = get_weather_data(JUAREZ_COORDS[0], JUAREZ_COORDS[1])
    
    if weather:
        st.metric("🌡️ Temperatura", f"{weather['main']['temp']}°C", f"Hum: {weather['main']['humidity']}%")
    
    if not df_incendios.empty:
        st.metric("Total Incidentes", len(df_incendios))
        st.caption(f"Zona más crítica: {df_incendios['colonia'].mode()[0]}")
        
        # Gráfica limpia
        st.markdown("##### Causas Frecuentes")
        st.bar_chart(df_incendios['causa'].value_counts().head(5))

# Footer minimalista
st.markdown("---")
st.markdown("<div style='text-align: center; color: grey;'>SAPRIA-FO © 2026</div>", unsafe_allow_html=True)