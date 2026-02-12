import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt

def render_3d_density_map(df):
    """Mapa Hexagonal 3D Táctico"""
    if df.empty:
        st.warning("Sin datos para renderizar mapa 3D.")
        return

    st.markdown("""
    <div style="background-color:#1F2937; padding:15px; border-radius:10px; border-left: 5px solid #FACC15; margin-bottom:20px;">
        <h4 style="color:white; margin:0;">🔥 Mapa de Calor Volumétrico</h4>
        <p style="color:#9CA3AF; font-size:12px; margin:0;">Visualización de densidad de incidentes acumulados.</p>
    </div>
    """, unsafe_allow_html=True)

    layer = pdk.Layer(
        "HexagonLayer",
        df,
        get_position=["lon", "lat"],
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        elevation_range=[0, 3000],
        extruded=True,
        coverage=1,
        radius=200,
        get_fill_color="[255, (1 - elevationValue / 500) * 255, 0, 180]", # Gradiente fuego
    )

    view_state = pdk.ViewState(
        longitude=-106.4856,
        latitude=31.7389,
        zoom=11,
        pitch=50, # Inclinación 3D
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Densidad de Focos: {elevationValue}"},
        map_style="mapbox://styles/mapbox/dark-v10"
    )
    
    st.pydeck_chart(r)

def render_tactical_charts(df):
    """Genera gráficas de tendencias con estilo SAPRIA"""
    if df.empty: return

    # Preparar datos
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['hora'] = pd.to_numeric(df['hora'], errors='coerce').fillna(0).astype(int)
    df['mes'] = df['fecha'].dt.month_name()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h5 style='color:#374151'>Incidencias por Hora del Día</h5>", unsafe_allow_html=True)
        chart_hora = alt.Chart(df).mark_bar(color='#374151').encode(
            x=alt.X('hora:O', title='Hora (0-24)'),
            y=alt.Y('count()', title='Focos'),
            tooltip=['hora', 'count()']
        ).properties(height=250)
        st.altair_chart(chart_hora, use_container_width=True)
        
    with col2:
        st.markdown("<h5 style='color:#374151'>Severidad de Incidentes</h5>", unsafe_allow_html=True)
        chart_sev = alt.Chart(df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("count()"),
            color=alt.Color("dano", scale=alt.Scale(scheme='goldorange'), title="Daño"),
            tooltip=["dano", "count()"]
        ).properties(height=250)
        st.altair_chart(chart_sev, use_container_width=True)