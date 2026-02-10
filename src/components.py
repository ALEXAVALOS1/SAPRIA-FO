import streamlit as st

# --- SOLO BRANDING, SIN ENLACES FALSOS ---
def render_top_navbar():
    st.markdown("""
    <div class="top-brand-bar">
        <i class="fa-solid fa-shield-halved yellow-text" style="font-size: 24px;"></i>
        <div style="margin-left:15px;">
            <span class="yellow-text">SAPRIA-FO</span> <span>Centro de Mando Municipal</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_map_floating_card(focos_activos, zona_critica):
    return f"""
    <div style="position: relative; height: 0; z-index: 1000;">
        <div class="floating-map-card">
            <div class="fmc-header"><i class="fa-solid fa-fire"></i> ESTATUS TÁCTICO</div>
            <div class="fmc-row"><span>Focos Históricos:</span> <span class="fmc-val">{focos_activos}</span></div>
            <div class="fmc-row"><span>Zona Caliente:</span> <span class="fmc-val">{str(zona_critica)[:15]}...</span></div>
            <div class="fmc-row"><span>Unidades:</span> <span class="fmc-val">3 Desplegadas</span></div>
        </div>
    </div>
    """

def render_risk_card(nivel, descripcion):
    colors = {"BAJO": "#10B981", "MODERADO": "#3B82F6", "ALTO": "#F59E0B", "MUY ALTO": "#F97316", "EXTREMO": "#E11D48"}
    color = colors.get(nivel, "#9CA3AF")
    return f"""
    <div class="dark-card">
        <div class="dc-title"><i class="fa-solid fa-circle-info"></i> NIVEL DE RIESGO</div>
        <div class="dc-value" style="color:{color}; display:flex; align-items:center; gap:10px;">
            <div style="width:12px; height:12px; border-radius:50%; background:{color}; box-shadow: 0 0 10px {color};"></div>
            {nivel}
        </div>
        <div style="font-size:11px; color:#94A3B8; margin-top:5px;">{descripcion}</div>
    </div>
    """

def render_small_stat(titulo, valor, icono, color):
    return f"""
    <div class="dark-card" style="padding:15px;">
        <div class="dc-title" style="color:{color}; margin-bottom:5px;"><i class="fa-solid {icono}"></i> {titulo}</div>
        <div class="dc-value" style="font-size:24px;">{valor}</div>
    </div>
    """

def render_nasa_card(df_nasa):
    anomalias = len(df_nasa) if not df_nasa.empty else 0
    color = "#EF4444" if anomalias > 0 else "#10B981"
    status = "¡FUEGO ACTIVO!" if anomalias > 0 else "Sin alertas satelitales"
    return f"""
    <div class="dark-card">
        <div class="dc-title" style="color:#3B82F6;"><i class="fa-solid fa-satellite"></i> ENLACE SATELITAL NASA</div>
        <div style="display:flex; align-items:center; gap:15px; margin-top:10px;">
            <div style="font-size:36px; font-weight:900; color:{color};">{anomalias}</div>
            <div style="font-size:12px; color:#94A3B8;"><b>{status}</b><br>Satélite VIIRS (24h)</div>
        </div>
    </div>
    """

def render_tactical_card(route_data, station_name):
    if not route_data: return ""
    return f"""
    <div class="dark-card" style="border:1px solid #3B82F6;">
        <div class="dc-title" style="color:#3B82F6;">LOGÍSTICA DE RESPUESTA</div>
        <div class="dc-value" style="color:#F8FAFC;">{route_data['duration']} min</div>
        <div style="font-size:11px; color:#94A3B8;">Unidad asignada: {station_name}</div>
    </div>
    """

def render_forecast_section():
    items = [
        ("06:00 p.m.", "fa-cloud-sun", "19°", "#F59E0B"), ("09:00 p.m.", "fa-cloud-moon", "14°", "#94A3B8"),
        ("12:00 a.m.", "fa-moon", "9°", "#94A3B8"), ("03:00 a.m.", "fa-moon", "9°", "#94A3B8"),
        ("06:00 a.m.", "fa-cloud-sun", "9°", "#F59E0B"), ("09:00 a.m.", "fa-sun", "14°", "#F59E0B")
    ]
    html = '<div class="forecast-section"><div style="font-size:11px; color:#64748B; font-weight:700; margin-bottom:15px; display:flex; justify-content:space-between;"><span><i class="fa-regular fa-clock"></i> PRONÓSTICO 12 HORAS</span><span>Fuente: OpenWeather</span></div><div class="forecast-container">'
    for time, icon, temp, col in items:
        html += f'<div class="forecast-item"><div class="fc-time">{time}</div><i class="fa-solid {icon} fc-icon" style="color:{col};"></i><div class="fc-temp">{temp}</div><div style="margin-top:5px;"><span class="fc-badge" style="color:#10B981; background:rgba(16,185,129,0.1);">BAJO</span></div></div>'
    html += '</div></div>'
    return html

def render_air_quality_card(aqi_data):
    if not aqi_data: return ""
    return f"""
    <div class="dark-card">
        <div class="dc-title">CALIDAD DEL AIRE</div>
        <div style="display:flex; justify-content:space-between; align-items:end; margin-bottom:5px;">
            <div style="font-size:20px; font-weight:900; color:{aqi_data['color']};">{aqi_data['texto']}</div>
            <div style="font-size:11px; color:#94A3B8;">PM2.5: {aqi_data['pm2_5']}</div>
        </div>
    </div>
    """