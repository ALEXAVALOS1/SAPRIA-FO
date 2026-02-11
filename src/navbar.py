import streamlit as st

def render_navbar():
    # 1. EL FONDO OSCURO (HTML PURO)
    st.markdown('<div class="fixed-header"></div>', unsafe_allow_html=True)

    # 2. LOS CONTROLES (FLOTANDO ENCIMA)
    with st.container():
        # CSS para forzar la posición de los controles
        st.markdown("""<style>div[data-testid="stVerticalBlock"] > div:first-child {position: fixed; top: 0; left: 0; right: 0; z-index: 1000; padding: 10px 20px;}</style>""", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 5, 2])
        
        with c1:
            # LOGO SIN ESPACIOS PARA EVITAR ERRORES
            st.markdown('<div style="display:flex;align-items:center;gap:10px;padding-top:10px;"><span class="material-icons-outlined" style="color:#FACC15;font-size:32px;">shield</span><div style="line-height:1;"><h1 style="color:white;font-weight:900;font-size:20px;margin:0;font-family:sans-serif;">SAPRIA-FO</h1><p style="color:#D1D5DB;font-size:9px;font-weight:600;letter-spacing:1px;margin:0;">MONITOREO MUNICIPAL</p></div></div>', unsafe_allow_html=True)
            
        with c2:
            # MENÚ CENTRADO
            st.markdown('<div style="margin-top:5px;"></div>', unsafe_allow_html=True)
            opciones = ["Dashboard Táctico", "Base Histórica", "Analítica 3D"]
            seleccion = st.radio("Nav", opciones, horizontal=True, label_visibility="collapsed")
            
        with c3:
            # BOTÓN DERECHA
            st.markdown('<div style="margin-top:5px;"></div>', unsafe_allow_html=True)
            col_spacer, col_btn = st.columns([1, 2])
            with col_btn:
                btn = st.button("📄 REPORTE", use_container_width=True)

    # ESPACIADOR PARA QUE EL CONTENIDO NO QUEDE OCULTO
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    
    page = "Dashboard"
    if "Base" in seleccion: page = "Base"
    elif "Analítica" in seleccion: page = "Analitica"
    
    return page, btn