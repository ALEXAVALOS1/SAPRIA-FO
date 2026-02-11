import streamlit as st

def render_navbar():
    """
    Renderiza la barra de navegación superior fija.
    """
    # 1. Fondo Oscuro Fijo (HTML Puro)
    st.markdown('<div class="fixed-header"></div>', unsafe_allow_html=True)

    # 2. Controles de Streamlit (Flotando encima)
    with st.container():
        # CSS para posicionar los controles sobre el fondo
        st.markdown("""
            <style>
                div[data-testid="stVerticalBlock"] > div:first-child {
                    position: fixed; top: 0; left: 0; right: 0; z-index: 100000; padding: 10px 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 5, 2], gap="small")

        # LOGO (HTML Compacto para evitar errores)
        with col1:
            st.markdown("""<div style="display:flex;align-items:center;gap:10px;padding-top:5px;"><span class="material-icons-outlined" style="color:#FACC15;font-size:36px;">shield</span><div style="line-height:1.1;"><h1 style="color:white;font-weight:900;font-size:22px;margin:0;font-family:'Montserrat';">SAPRIA-FO</h1><p style="color:#D1D5DB;font-size:9px;font-weight:600;letter-spacing:1.5px;margin:0;">MONITOREO MUNICIPAL</p></div></div>""", unsafe_allow_html=True)

        # MENÚ
        with col2:
            opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
            seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")

        # BOTÓN
        with col3:
            c_spacer, c_btn = st.columns([1, 2])
            with c_btn:
                btn = st.button("📄 REPORTE PDF", use_container_width=True)

    # Espaciador invisible
    st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)
    
    # Lógica de retorno
    page = "Dashboard"
    if "Base" in seleccion: page = "Base"
    elif "Analítica" in seleccion: page = "Analitica"
    
    return page, btn