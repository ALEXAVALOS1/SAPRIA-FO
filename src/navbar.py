import streamlit as st

def render_navbar():
    # 1. Dibujamos el fondo negro fijo
    st.markdown('<div class="fixed-header"></div>', unsafe_allow_html=True)

    # 2. Ponemos los elementos encima (Logo, Menú, Botón)
    with st.container():
        # CSS Hack para subir el nivel de los controles
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] > div:first-child {
                position: fixed; top: 0; left: 0; right: 0; z-index: 100000; padding: 15px 40px;
            }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 5, 2], gap="medium")

        # LOGO SAPRIA
        with col1:
            # HTML SIN ESPACIOS AL INICIO PARA EVITAR ERRORES
            html_logo = """<div style="display:flex;align-items:center;gap:12px;">
<span class="material-icons-outlined" style="color:#FACC15;font-size:38px;">shield</span>
<div style="line-height:1;"><h1 style="color:white;font-weight:900;font-size:24px;margin:0;font-family:'Montserrat';">SAPRIA-FO</h1>
<p style="color:#D1D5DB;font-size:10px;font-weight:600;letter-spacing:2px;margin:0;">MONITOREO MUNICIPAL</p></div></div>"""
            st.markdown(html_logo, unsafe_allow_html=True)

        # MENÚ
        with col2:
            opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
            seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")

        # BOTÓN
        with col3:
            c_a, c_b = st.columns([1, 2])
            with c_b:
                btn = st.button("📄 REPORTE PDF", use_container_width=True)

    # Espaciador invisible para bajar el contenido real
    st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)
    
    # Lógica de retorno
    page = "Dashboard"
    if "Base" in seleccion: page = "Base"
    elif "Analítica" in seleccion: page = "Analitica"
    
    return page, btn