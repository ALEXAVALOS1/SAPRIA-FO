import streamlit as st

def render_navbar():
    """
    Dibuja la barra superior fija y controla la navegación.
    """
    # 1. Fondo Oscuro Fijo (HTML)
    st.markdown('<div class="fixed-header"></div>', unsafe_allow_html=True)

    # 2. Contenedor de Controles (Streamlit)
    with st.container():
        # CSS para elevar los controles sobre el fondo
        st.markdown("""
            <style>
                div[data-testid="stVerticalBlock"] > div:first-child {
                    position: fixed; top: 0; left: 0; right: 0; z-index: 9999; padding: 15px 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 5, 2], gap="small")

        # LOGO
        with col1:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="material-icons-outlined" style="color: #FACC15; font-size: 32px;">shield</span>
                <div style="line-height: 1.1;">
                    <h1 style="color: white; font-weight: 900; font-size: 20px; margin: 0; font-family: 'Montserrat';">SAPRIA-FO</h1>
                    <p style="color: #D1D5DB; font-size: 9px; font-weight: 600; letter-spacing: 1.5px; margin: 0;">MONITOREO MUNICIPAL</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # MENÚ
        with col2:
            opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
            seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")

        # BOTÓN
        with col3:
            col_a, col_b = st.columns([1, 1.5])
            with col_b:
                btn = st.button("📄 REPORTE PDF", use_container_width=True)

    # Espacio para empujar el contenido real hacia abajo
    st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)
    
    # Retorno simple
    page = "Dashboard"
    if "Base" in seleccion: page = "Base"
    elif "Analítica" in seleccion: page = "Analitica"
    
    return page, btn