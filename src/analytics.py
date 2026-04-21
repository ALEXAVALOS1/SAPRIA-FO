import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt

def render_tactical_dashboard(df):
    """
    Renderiza el tablero de inteligencia histórica.
    """
    if df.empty:
        st.warning("No hay datos históricos.")
        return df

    data = df.copy()
    data['fecha'] = pd.to_datetime(data['fecha'])

    # Filtros de fecha estándar...
    st.markdown("""
    <div style="background-color:white; padding:15px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:20px;">
        <h4 style="color:#374151; margin:0 0 10px 0; font-size:14px; font-weight:bold;">🔎 FILTROS DE TIEMPO</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        min_date = data['fecha'].min().date()
        max_date = data['fecha'].max().date()
        date_range = st.date_input("Rango de Fechas", [min_date, max_date])

    if len(date_range) == 2:
        mask = (data['fecha'].dt.date >= date_range[0]) & (data['fecha'].dt.date <= date_range[1])
        data = data.loc[mask]

    return data

def render_3d_density_map(df):
    if df.empty:
        st.info("Sin datos para el mapa.")
        return

    st.markdown("""
    <div style="background-color:#1F2937; padding:15px; border-radius:10px; border-left: 5px solid #FACC15; margin-top:20px; margin-bottom:20px;">
        <h4 style="color:white; margin:0; font-size:16px;">🗺️ Mapa Híbrido: Puntos Exactos + Densidad</h4>
        <p style="color:#9CA3AF; font-size:12px; margin:0;">Los puntos muestran ubicación exacta. Los hexágonos muestran zonas de calor.</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. AUTOCENTRADO INTELIGENTE
    # Calculamos el centro promedio de los puntos visibles para que "salgan todos"
    mid_lat = df['lat'].mean()
    mid_lon = df['lon'].mean()

    # 2. DEFINIR COLORES SEMÁFORO (Rojo, Amarillo, Verde)
    # Si tienes columna 'dano', la usamos. Si no, todo rojo por defecto.
    def get_color(dano):
        if isinstance(dano, str):
            if 'Total' in dano or 'Alto' in dano: return [255, 0, 0, 200]   # Rojo
            if 'Medio' in dano: return [255, 255, 0, 200] # Amarillo
        return [0, 255, 0, 200] # Verde (Bajo/Parcial)

    # Asignamos color a cada fila
    df['color'] = df['dano'].apply(get_color)

    # --- CAPA 1: PUNTOS EXACTOS (SCATTERPLOT) ---
    # Esto soluciona que "no salgan todos". Aquí ves cada punto individual.
    layer_puntos = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=80,          # Tamaño del punto
        pickable=True,          # Para que salga el tooltip
        opacity=0.9,
        stroked=True,
        filled=True,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )

    # --- CAPA 2: HEXÁGONOS (MODIFICADA: ANCHA Y BAJA) ---
    layer_hex = pdk.Layer(
        "HexagonLayer",
        df,
        get_position=["lon", "lat"],
        auto_highlight=True,
        elevation_scale=5,      # <--- MÁS BAJAS (Antes 30)
        pickable=False,         # Dejamos el click para los puntos, no los hexágonos
        elevation_range=[0, 500],
        extruded=True,
        coverage=1,
        radius=150,             # <--- MÁS ANCHAS (Antes 30)
        opacity=0.3,            # <--- TRANSPARENTE para ver los puntos abajo
        # Gradiente Semáforo para la densidad
        color_range=[
            [0, 255, 0, 150],   # Verde
            [255, 255, 0, 150], # Amarillo
            [255, 0, 0, 150]    # Rojo
        ],
    )

    view_state = pdk.ViewState(
        longitude=mid_lon,      # Centrado automático
        latitude=mid_lat,
        zoom=11,
        pitch=30,               # Menos inclinación para ver mejor los puntos
    )

    # Tooltip mejorado con Coordenadas
    tooltip = {
        "html": "<b>Incidente Detectado</b><br/>"
                "📍 Lat: {lat}<br/>"
                "📍 Lon: {lon}<br/>"
                "💥 Daño: {dano}<br/>"
                "📅 Fecha: {fecha}",
        "style": {"backgroundColor": "#1F2937", "color": "white", "fontSize": "12px"}
    }

    r = pdk.Deck(
        layers=[layer_hex, layer_puntos], # Dibujamos puntos encima o hexágonos encima según orden
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=pdk.map_styles.CARTO_DARK
    )
    
    st.pydeck_chart(r)