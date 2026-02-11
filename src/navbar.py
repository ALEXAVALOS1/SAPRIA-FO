import streamlit as st

def render_navbar():
    """
    Renderiza la barra de navegación superior fija y devuelve la selección.
    """
    # 1. Dibujamos el fondo oscuro fijo (HTML puro)
    st.markdown('<div class="fixed-header"></div>', unsafe_allow_html=True)

    # 2. Ponemos los controles ENCIMA del fondo
    # Usamos un contenedor para alinear todo
    with st.container():
        # CSS hack para elevar el z-index de estos controles
        st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] > div:first-child {
                position: fixed; top: 0; left: 0; right: 0; z-index: 10000; padding: 0 2rem;
            }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 5, 2])

        # LOGO (Izquierda)
        with col1:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px; padding-top: 15px;">
                <span class="material-icons-outlined" style="color: #FACC15; font-size: 36px;">shield</span>
                <div style="line-height: 1;">
                    <h1 style="color: white; font-weight: 900; font-size: 22px; margin: 0; font-family: 'Montserrat';">SAPRIA-FO</h1>
                    <p style="color: #D1D5DB; font-size: 9px; font-weight: 600; letter-spacing: 1.5px; margin: 0;">MONITOREO MUNICIPAL</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # MENÚ (Centro)
        with col2:
            opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
            seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")

        # BOTÓN (Derecha)
        with col3:
            col_spacer, col_b = st.columns([1, 2])
            with col_b:
                btn_reporte = st.button("📄 REPORTE PDF", use_container_width=True)

    # Espaciador para empujar el contenido hacia abajo
    st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)

    # Retorno de variables
    pagina = "Dashboard"
    if "Base" in seleccion: pagina = "Base"
    elif "Analítica" in seleccion: pagina = "Analitica"
    
    return pagina, btn_reporte