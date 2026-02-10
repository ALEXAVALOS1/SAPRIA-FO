import streamlit as st
import pydeck as pdk
import plotly.express as px
import pandas as pd

def render_3d_density_map(df):
    """Genera un mapa 3D de hexágonos estilo Cyberpunk."""
    if df.empty: return
    
    st.markdown("<h3 style='color:#F8FAFC; margin-bottom:15px;'><i class='fa-solid fa-cube' style='color:#3B82F6;'></i> Topografía de Riesgo 3D</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:13px;'>Análisis de densidad volumétrica de incidentes históricos.</p>", unsafe_allow_html=True)

    # Configuración de la capa 3D (Hexágonos)
    layer = pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position=["lon", "lat"],
        radius=300, # Tamaño del hexágono en metros
        elevation_scale=50, # Qué tan alto crece la torre
        elevation_range=[0, 1000],
        extruded=True,
        get_fill_color="[225, 29, 72, 200]", # Rojo SAPRIA con transparencia
        pickable=True,
        auto_highlight=True
    )

    # Inclinación de la cámara (pitch) para ver el 3D
    view_state = pdk.ViewState(
        latitude=31.7389, 
        longitude=-106.4856, 
        zoom=10.5, 
        pitch=50, 
        bearing=-15
    )

    # Renderizar el mapa
    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state, 
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "Concentración Crítica: {elevationValue} incidentes"}
    )
    
    st.pydeck_chart(r, use_container_width=True)

def render_statistics(df):
    """Genera gráficos interactivos con Plotly en modo oscuro."""
    if df.empty: return
    
    st.markdown("<h3 style='color:#F8FAFC; margin-bottom:15px; margin-top:30px;'><i class='fa-solid fa-chart-pie' style='color:#F59E0B;'></i> Análisis Estadístico</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Barras: Top 10 Colonias
        top_colonias = df['colonia'].value_counts().head(10).reset_index()
        top_colonias.columns = ['Colonia', 'Incidentes']
        
        fig_bar = px.bar(
            top_colonias, x='Incidentes', y='Colonia', orientation='h',
            title='Top 10 Zonas Críticas',
            color='Incidentes', color_continuous_scale='Reds'
        )
        fig_bar.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis={'categoryorder':'total ascending'}, font=dict(family="Inter", color="#94A3B8")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        # Gráfico de Dona: Tipos de Incidente
        tipo_inc = df['tipo_incidente'].value_counts().reset_index()
        tipo_inc.columns = ['Tipo', 'Cantidad']
        
        fig_pie = px.pie(
            tipo_inc, values='Cantidad', names='Tipo', hole=0.6,
            title='Distribución por Tipo de Evento',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig_pie.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", color="#94A3B8")
        )
        st.plotly_chart(fig_pie, use_container_width=True)