import streamlit as st

def render_navbar():
    # 1. ESTILOS CSS INYECTADOS DIRECTAMENTE (Para asegurar que carguen)
    st.markdown("""
        <style>
            .navbar-container {
                position: fixed; top: 0; left: 0; right: 0; height: 80px;
                background-color: #374151; z-index: 99999;
                border-bottom: 3px solid #FACC15; display: flex; align-items: center;
                padding: 0 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
            .nav-logo { font-family: sans-serif; font-weight: 900; font-size: 22px; color: white; display: flex; align-items: center; gap: 10px; }
            .nav-logo span { color: #D1D5DB; font-size: 10px; letter-spacing: 2px; display: block; }
            
            /* FORZAR ST.RADIO A FLOTAR */
            div[data-testid="stVerticalBlock"] > div:first-child {
                position: fixed; top: 0; left: 0; right: 0; z-index: 100000;
                background: transparent; pointer-events: none;
            }
            /* Habilitar clicks en el menú */
            div[data-testid="stRadio"], div[data-testid="stButton"] { pointer-events: auto; }
            
            .spacer { height: 100px; }
        </style>
        <div class="navbar-container">
            <div class="nav-logo">
                <span class="material-icons-outlined" style="color:#FACC15; font-size: 30px; margin-right:5px;">shield</span>
                <div>SAPRIA-FO<span>MONITOREO MUNICIPAL</span></div>
            </div>
        </div>
        <div class="spacer"></div>
    """, unsafe_allow_html=True)

    # 2. CONTROLES DE STREAMLIT (Flotantes)
    # Usamos columnas invisibles para posicionar los botones sobre la barra HTML
    c1, c2, c3 = st.columns([3, 5, 2])
    
    with c2:
        # MENÚ CENTRADO
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
        seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")
    
    with c3:
        # BOTÓN DERECHA
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        btn = st.button("📄 REPORTE PDF", use_container_width=True)

    page = "Dashboard"
    if "Base" in seleccion: page = "Base"
    elif "Analítica" in seleccion: page = "Analitica"

    return page, btn