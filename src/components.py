import streamlit as st

def render_top_navbar():
    st.markdown("""
    <div class="top-brand-bar">
        <div style="display:flex; align-items:center; gap:10px;">
            <i class="fa-solid fa-shield-halved" style="color:#E11D48; font-size: 18px;"></i>
            <span>SAPRIA-FO Monitor Municipal Juárez</span>
        </div>
        <div class="nav-links">
            <span>Dashboard</span> <span>Reportes</span> <span>Alertas</span> <span>Prevención</span> <span>Ayuda</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_map_floating_card(focos_activos, zona_critica):
    return f"""
    <div style="position: relative; height: 0; z-index: 1000;">
        <div class="floating-map-card">
            <div class="fmc-header"><i class="fa-solid fa-location-crosshairs"></i> ESTATUS TÁCTICO</div>
            <div class="fmc-row"><span>Focos Históricos:</span> <span class="fmc-val" style="color:#E11D48;">{focos_activos}</span></div>
            <div class="fmc-row"><span>Zona Caliente:</span> <span class="fmc-val">{str(zona_critica)[:15]}...</span></div>
            <div class="fmc-row"><span>Unidades:</span> <span class="fmc-val">3 Desplegadas</span></div>
        </div>
    </div>
    """

def render_risk_card(nivel, descripcion):
    colors = {"BAJO": "#10B981", "MODERADO": "#3B82F6", "ALTO": "#F59E0B", "MUY ALTO": "#F97316", "EXTREMO": "#E11D48"}
    color = colors.get(nivel, "#9CA3AF")
    return f"""
    <div class="dark-card" style="border-top: 4px solid {color};">
        <div class="dc-title"><i class="fa-solid fa-circle-info"></i> NIVEL DE RIESGO (FWI)</div>
        <div class="dc-value" style="color:{color};">{nivel}</div>
        <div style="font-size:11px; color:#94A3B8; margin-top:5px;">{descripcion}</div>
    </div>
    """

def render_small_stat(titulo, valor, icono, color):
    return f"""
    <div class="dark-card" style="padding:15px; display:flex; align-items:center; gap:15px;">
        <div style="background:rgba(255,255,255,0.05); width:40px; height:40px; display:flex; justify-content:center; align-items:center; border-radius:8px; color:{color}; font-size:18px;">
            <i class="fa-solid {icono}"></i>
        </div>
        <div>
            <div class="dc-title" style="margin-bottom:0;">{titulo}</div>
            <div class="dc-value" style="font-size:20px;">{valor}</div>
        </div>
    </div>
    """

def render_nasa_card(df_nasa):
    anomalias = len(df_nasa) if not df_nasa.empty else 0
    color = "#EF4444" if anomalias > 0 else "#10B981"
    status = "¡ANOMALÍA TÉRMICA!" if anomalias > 0 else "Sin alertas satelitales"
    pulse = "animation: pulse-red 2s infinite;" if anomalias > 0 else ""
    return f"""
    <div class="dark-card" style="border-left: 4px solid #3B82F6; {pulse}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="dc-title" style="color:#3B82F6; margin:0;"><i class="fa-solid fa-satellite fa-fade"></i> ENLACE SATELITAL NASA</div>
            <div style="font-size:9px; background:rgba(59,130,246,0.2); color:#3B82F6; padding:2px 6px; border-radius:4px;">LIVE 24H</div>
        </div>
        <div style="display:flex; align-items:center; gap:15px; margin-top:10px;">
            <div style="font-size:32px; font-weight:900; color:{color};">{anomalias}</div>
            <div style="font-size:11px; color:#94A3B8;"><b style="color:{color};">{status}</b><br>Escaneo Infrarrojo VIIRS.</div>
        </div>
    </div>
    """

def render_tactical_card(route_data, station_name):
    if not route_data: return ""
    return f"""
    <div class="dark-card" style="border: 1px solid #3B82F6; background: rgba(59, 130, 246, 0.05);">
        <div class="dc-title" style="color:#3B82F6;"><i class="fa-solid fa-route"></i> LOGÍSTICA DE RESPUESTA</div>
        <div class="dc-value" style="color:#10B981;">{route_data['duration']} min</div>
        <div style="font-size:11px; color:#94A3B8;">Unidad asignada: {station_name}</div>
    </div>
    """

def render_forecast_section():
    items = [
        ("06:00 p.m.", "fa-cloud-sun", "19°", "#10B981"), ("09:00 p.m.", "fa-cloud-moon", "14°", "#10B981"),
        ("12:00 a.m.", "fa-moon", "9°", "#10B981"), ("03:00 a.m.", "fa-moon", "9°", "#10B981"),
        ("06:00 a.m.", "fa-cloud-sun", "9°", "#F59E0B"), ("09:00 a.m.", "fa-sun", "14°", "#10B981")
    ]
    html = '<div class="forecast-section"><div style="font-size:10px; color:#94A3B8; font-weight:700; margin-bottom:15px; text-transform:uppercase;">Pronóstico de Riesgo (Próximas 12 horas)</div><div class="forecast-container">'
    for time, icon, temp, col in items:
        html += f'<div class="forecast-item"><div class="fc-time">{time}</div><i class="fa-solid {icon} fc-icon" style="color:{col};"></i><div class="fc-temp">{temp}</div><span class="fc-badge">BAJO</span></div>'
    html += '</div></div>'
    return html

def render_air_quality_card(aqi_data):
    if not aqi_data: return ""
    return f"""
    <div class="dark-card">
        <div class="dc-title">CALIDAD DEL AIRE (AQI)</div>
        <div style="display:flex; justify-content:space-between; align-items:end;">
            <div style="font-size:24px; font-weight:900; color:{aqi_data['color']};">{aqi_data['texto']}</div>
            <div style="font-size:10px; color:#94A3B8;">PM2.5: {aqi_data['pm2_5']}</div>
        </div>
        <div style="height:4px; background:#334155; border-radius:2px; margin-top:10px;">
            <div style="width:{min(aqi_data['aqi']*20, 100)}%; height:100%; background:{aqi_data['color']}; border-radius:2px;"></div>
        </div>
    </div>
    """