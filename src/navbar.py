import streamlit as st

def render_navbar():
    """
    Dibuja la barra de navegación superior fija.
    Retorna: La página seleccionada (str) y si se presionó el botón de reporte (bool).
    """
    # 1. Dibujamos el fondo oscuro fijo usando HTML
    st.markdown('<div class="header-container"></div>', unsafe_allow_html=True)

    # 2. Usamos columnas de Streamlit ENCIMA del fondo oscuro
    # Usamos un contenedor vacío con padding para bajar los elementos visuales al nivel correcto
    with st.container():
        col_logo, col_menu, col_btn = st.columns([2, 5, 2])

        # --- LOGO (Izquierda) ---
        with col_logo:
            st.markdown("""
            <div style="position: fixed; top: 15px; left: 30px; z-index: 1000; display: flex; align-items: center; gap: 10px;">
                <span class="material-icons-outlined" style="color: #FACC15; font-size: 35px;">shield</span>
                <div style="line-height: 1;">
                    <h1 style="color: white; font-weight: 900; font-size: 24px; margin: 0; font-family: 'Montserrat';">SAPRIA-FO</h1>
                    <p style="color: #9CA3AF; font-size: 9px; font-weight: 600; letter-spacing: 2px; margin: 0;">MONITOREO MUNICIPAL</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- MENÚ (Centro) ---
        # El CSS en style.css se encarga de posicionar esto 'fixed' visualmente o ajustarlo
        with col_menu:
            # Truco: st.radio nativo de Streamlit para manejar la lógica
            opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
            seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")

        # --- BOTÓN (Derecha) ---
        with col_btn:
            # Alineamos el botón a la derecha
            c1, c2 = st.columns([1, 2])
            with c2:
                btn_reporte = st.button("📄 REPORTE PDF", use_container_width=True)

    # Espaciador invisible para que el contenido de la página no quede oculto bajo la barra
    st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)

    # Lógica de retorno
    if "Dashboard" in seleccion: return "Dashboard", btn_reporte
    elif "Base" in seleccion: return "Base", btn_reporte
    elif "Analítica" in seleccion: return "Analitica", btn_reporte
    return "Dashboard", btn_reporte