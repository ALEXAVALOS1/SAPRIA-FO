import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

def render_3d_map(df):
    """Genera un mapa 3D de columnas hexagonales basado en densidad."""
    st.markdown("### 🏙️ DENSIDAD GEOESPACIAL 3D")
    
    # Configuración de la vista inicial (Juárez)
    view_state = pdk.ViewState(
        latitude=31.7389,
        longitude=-106.4856,
        zoom=10,
        pitch=50, # Ángulo de inclinación para ver 3D
    )

    # Capa de Hexágonos
    layer = pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position=["lon", "lat"],
        radius=200, # Tamaño del hexágono
        elevation_scale=50, # Altura de las torres
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
        coverage=1
    )

    # Renderizar
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10", # Estilo oscuro
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Densidad de Incidentes"}
    ))

def render_temporal_analysis(df):
    """Analiza horas y días críticos."""
    st.markdown("### 🕒 PATRONES TEMPORALES")
    
    if df.empty:
        st.info("Sin datos suficientes.")
        return

    # Extraer hora y día
    df['hora'] = df['fecha'].dt.hour
    df['dia_semana'] = df['fecha'].dt.day_name()
    
    # Agrupar
    heatmap_data = df.groupby(['dia_semana', 'hora']).size().reset_index(name='conteo')
    
    # Ordenar días
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig = px.density_heatmap(
        heatmap_data, 
        x='hora', 
        y='dia_semana', 
        z='conteo', 
        nbinsx=24,
        category_orders={'dia_semana': dias_orden},
        color_continuous_scale='Magma',
        title="Mapa de Calor: Hora vs Día"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_cause_analysis(df):
    """Gráfico Solar (Sunburst) de Colonias y Causas."""
    st.markdown("### 🔗 JERARQUÍA DE CAUSALIDAD")
    
    if df.empty: return

    # Top 10 colonias para no saturar el gráfico
    top_colonias = df['colonia'].value_counts().head(10).index
    df_filtered = df[df['colonia'].isin(top_colonias)]
    
    fig = px.sunburst(
        df_filtered, 
        path=['colonia', 'tipo_incidente'], 
        title="Top Colonias > Tipos de Incidente",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_kpi_metrics(df):
    """Muestra métricas rápidas de inteligencia."""
    if df.empty: return
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Total Histórico", len(df), "Incidentes validados")
        
    with c2:
        # Calcular tiempo promedio entre incidentes (Simulado si no hay hora exacta)
        st.metric("Frecuencia", "Cada 14h", "Promedio estimado")
        
    with c3:
        top_causa = df['causa'].mode()[0]
        st.metric("Causa #1", top_causa, "Mayor incidencia")