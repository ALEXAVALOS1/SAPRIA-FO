import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt

def render_tactical_dashboard(df):
    """
    Renderiza el tablero de inteligencia histórica con filtros y gráficas.
    """
    if df.empty:
        st.warning("No hay datos históricos para analizar.")
        return df

    # 1. COPIA SEGURA DE DATOS
    data = df.copy()
    
    # 2. ARREGLO DEL ERROR DE HORA (CRÍTICO)
    # Convertimos a fecha real
    data['fecha'] = pd.to_datetime(data['fecha'])
    
    # EXTRAEMOS LA HORA DIRECTAMENTE DE LA FECHA (Esto evita el KeyError)
    data['hora_clean'] = data['fecha'].dt.hour
    
    # Día de la semana
    dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    data['dia_num'] = data['fecha'].dt.dayofweek
    data['dia_nombre'] = data['dia_num'].map(dias_es)

    # 3. FILTROS DE INTELIGENCIA
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

    # Filtrar datos
    if len(date_range) == 2:
        mask = (data['fecha'].dt.date >= date_range[0]) & (data['fecha'].dt.date <= date_range[1])
        data = data.loc[mask]

    # 4. GRÁFICAS ESTRATÉGICAS
    col_g1, col_g2 = st.columns(2, gap="medium")

    with col_g1:
        st.markdown("<h5 style='color:#374151; font-size:12px; font-weight:bold; text-align:center'>🔥 LA HORA DEL DIABLO (Incidentes por Hora)</h5>", unsafe_allow_html=True)
        chart_hora = alt.Chart(data).mark_bar(color='#374151', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('hora_clean:O', title='Hora (0-24h)'),
            y=alt.Y('count()', title='Focos'),
            tooltip=['hora_clean', 'count()']
        ).properties(height=220)
        st.altair_chart(chart_hora, use_container_width=True)

    with col_g2:
        st.markdown("<h5 style='color:#374151; font-size:12px; font-weight:bold; text-align:center'>📅 DÍAS DE ALTO RIESGO</h5>", unsafe_allow_html=True)
        chart_dia = alt.Chart(data).mark_bar(color='#FACC15').encode(
            x=alt.X('dia_nombre:N', sort=['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'], title='Día'),
            y=alt.Y('count()', title='Incidentes'),
            tooltip=['dia_nombre', 'count()']
        ).properties(height=220)
        st.altair_chart(chart_dia, use_container_width=True)

    return data

def render_3d_density_map(df):
    if df.empty:
        st.info("Sin datos para mostrar en el mapa 3D.")
        return

    st.markdown("""
    <div style="background-color:#1F2937; padding:15px; border-radius:10px; border-left: 5px solid #FACC15; margin-top:20px; margin-bottom:20px;">
        <h4 style="color:white; margin:0; font-size:16px;">🗺️ Mapa Volumétrico de Calor</h4>
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
        get_fill_color="[255, (1 - elevationValue / 500) * 255, 0, 180]",
    )

    view_state = pdk.ViewState(
        longitude=-106.4856,
        latitude=31.7389,
        zoom=10.5,
        pitch=50,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Densidad: {elevationValue}"},
        map_style="mapbox://styles/mapbox/dark-v10"
    )
    
    st.pydeck_chart(r)