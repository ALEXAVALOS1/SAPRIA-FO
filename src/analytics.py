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

    # 1. COPIA SEGURA Y EXTRACCIÓN DE FECHAS
    data = df.copy()
    data['fecha'] = pd.to_datetime(data['fecha'])

    # MESES
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    data['mes_num'] = data['fecha'].dt.month
    data['mes_nombre'] = data['mes_num'].map(meses_es)

    # DÍAS
    dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    data['dia_num'] = data['fecha'].dt.dayofweek
    data['dia_nombre'] = data['dia_num'].map(dias_es)

    # 2. FILTROS
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

    # 3. GRÁFICAS ESTRATÉGICAS
    col_g1, col_g2 = st.columns(2, gap="medium")

    with col_g1:
        st.markdown("<h5 style='color:#374151; font-size:12px; font-weight:bold; text-align:center'>📅 TENDENCIA MENSUAL (Temporada de Riesgo)</h5>", unsafe_allow_html=True)
        chart_mes = alt.Chart(data).mark_bar(color='#374151', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('mes_nombre:N', sort=list(meses_es.values()), title='Mes'),
            y=alt.Y('count()', title='Incidentes'),
            tooltip=['mes_nombre', 'count()']
        ).properties(height=220)
        st.altair_chart(chart_mes, use_container_width=True)

    with col_g2:
        st.markdown("<h5 style='color:#374151; font-size:12px; font-weight:bold; text-align:center'>📆 DÍAS DE ALTO RIESGO</h5>", unsafe_allow_html=True)
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
        <h4 style="color:white; margin:0; font-size:16px;">🗺️ Mapa Táctico de Densidad</h4>
        <p style="color:#9CA3AF; font-size:12px; margin:0;">Zonas calientes basadas en el historial filtrado.</p>
    </div>
    """, unsafe_allow_html=True)

    # CAPA HEXAGONAL CALIBRADA
    layer = pdk.Layer(
        "HexagonLayer",
        df,
        get_position=["lon", "lat"],
        auto_highlight=True,
        # 1. BAJAMOS LA ESCALA DE ALTURA (Antes 30 -> Ahora 10)
        elevation_scale=10,
        pickable=True,
        # 2. ACOTAMOS EL RANGO PARA QUE LOS PEQUEÑOS NO DESAPAREZCAN
        elevation_range=[0, 1000], 
        extruded=True,
        coverage=1,
        radius=30, 
        # Color: Gradiente de Rojo a Amarillo (Más visible)
        get_fill_color="[255, (1 - elevationValue / 200) * 255, 0, 200]",
    )

    view_state = pdk.ViewState(
        longitude=-106.4856,
        latitude=31.7389,
        zoom=11,
        pitch=50, # Un poco más de inclinación para ver volumen
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Densidad: {elevationValue} incidentes"},
        map_style=pdk.map_styles.CARTO_DARK
    )
    
    st.pydeck_chart(r)