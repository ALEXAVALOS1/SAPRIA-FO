import streamlit as st

# --- 1. COMPONENTES VISUALES ---

def render_top_navbar():
    st.markdown("""
<div class="top-navbar">
    <div class="nav-brand">
        <i class="fa-solid fa-shield-halved" style="color: #E11D48; font-size: 20px;"></i>
        <span>SAPRIA-FO Monitor Municipal Juárez</span>
    </div>
    <div class="nav-links">
        <span class="nav-link active">Dashboard</span>
        <span class="nav-link">Reportes</span>
        <span class="nav-link">Alertas</span>
    </div>
</div>
""", unsafe_allow_html=True)

def render_map_floating_card(focos_activos, zona_critica):
    return f"""
<div style="position: relative; height: 0; z-index: 1000;">
    <div class="floating-map-card">
        <div class="fmc-header"><i class="fa-solid fa-location-crosshairs"></i> ESTATUS TÁCTICO</div>
        <div class="fmc-body">
            <div class="fmc-row"><span>Focos Históricos:</span> <span class="fmc-val" style="color:#E11D48;">{focos_activos}</span></div>
            <div class="fmc-row"><span>Zona Caliente:</span> <span class="fmc-val">{str(zona_critica)[:18]}...</span></div>
            <div class="fmc-row"><span>Unidades:</span> <span class="fmc-val">3 Desplegadas</span></div>
        </div>
    </div>
</div>
"""

def render_risk_card(nivel, descripcion):
    colors = {"BAJO": "#10B981", "MODERADO": "#3B82F6", "ALTO": "#F59E0B", "MUY ALTO": "#F97316", "EXTREMO": "#E11D48"}
    color = colors.get(nivel, "#9CA3AF")
    return f"""
<div class="dash-card" style="border-left: 4px solid {color}; padding: 15px;">
    <div style="font-size:10px; color:{color}; font-weight:bold;">NIVEL DE RIESGO</div>
    <div style="font-size:24px; color:white; font-weight:900;">{nivel}</div>
    <div style="font-size:11px; color:#94A3B8;">{descripcion}</div>
</div>
"""

def render_small_stat(titulo, valor, icono, color, bg_color):
    return f"""
<div class="dash-card" style="display:flex; align-items:center; gap:15px; padding:15px;">
    <div style="background:{bg_color}; width:40px; height:40px; display:flex; align-items:center; justify-content:center; border-radius:8px; color:{color}; font-size:18px;">
        <i class="fa-solid {icono}"></i>
    </div>
    <div>
        <div style="font-size:10px; color:#94A3B8; font-weight:bold;">{titulo}</div>
        <div style="font-size:20px; font-weight:bold;">{valor}</div>
    </div>
</div>
"""

def render_air_quality_card(aqi_data):
    if not aqi_data: return ""
    width = min(aqi_data['aqi'] * 20, 100)
    return f"""
<div class="dash-card">
    <div style="font-size:10px; color:#94A3B8; font-weight:bold; margin-bottom:10px;">CALIDAD DEL AIRE</div>
    <div style="display:flex; justify-content:space-between; align-items:end; margin-bottom:5px;">
        <div style="font-size:20px; font-weight:bold; color:{aqi_data['color']};">{aqi_data['texto']}</div>
        <div style="font-size:10px; color:#64748B;">PM2.5: {aqi_data['pm2_5']}</div>
    </div>
    <div style="height:4px; background:#334155; border-radius:2px;">
        <div style="width:{width}%; height:100%; background:{aqi_data['color']}; border-radius:2px;"></div>
    </div>
</div>
"""

def render_forecast_section():
    items = [
        ("06:00 p.m.", "fa-cloud-sun", "19°", "#10B981"),
        ("09:00 p.m.", "fa-cloud-moon", "14°", "#10B981"),
        ("12:00 a.m.", "fa-moon", "9°", "#10B981"),
        ("03:00 a.m.", "fa-moon", "9°", "#10B981"),
        ("06:00 a.m.", "fa-cloud-sun", "9°", "#F59E0B"),
        ("09:00 a.m.", "fa-sun", "14°", "#10B981")
    ]
    html = '<div class="forecast-section"><div style="font-size:10px; color:#94A3B8; font-weight:bold; margin-bottom:10px;">PRONÓSTICO 12 HORAS</div><div class="forecast-container">'
    for time, icon, temp, col in items:
        # Todo en una sola línea para que Streamlit no lo convierta en bloque de código
        html += f'<div class="forecast-item"><div class="fc-time">{time}</div><i class="fa-solid {icon} fc-icon" style="color:{col};"></i><div class="fc-temp">{temp}</div><span class="fc-badge" style="color:{col}; background:{col}20;">BAJO</span></div>'
    html += '</div></div>'
    return html

# --- 2. FUNCIONES TÁCTICAS ---

def render_tactical_card(route_data, station_name):
    if not route_data: return ""
    return f"""
<div class="dash-card" style="border: 1px solid #3B82F6; background: rgba(59, 130, 246, 0.1); margin-bottom:15px;">
    <div style="color:#3B82F6; font-weight:bold; font-size:10px; margin-bottom:5px;">LOGÍSTICA</div>
    <div style="font-size:22px; font-weight:bold;">{route_data['duration']} min</div>
    <div style="font-size:11px; opacity:0.7;">Unidad: {station_name}</div>
</div>
"""

def render_simulation_controls(wind_speed, wind_deg):
    st.markdown(f"""
<div style="background:rgba(225, 29, 72, 0.1); padding:15px; border-radius:12px; border:1px solid #E11D48; margin-bottom:15px;">
    <div style="font-size:10px; color:#E11D48; font-weight:bold;">MODELO DE PROPAGACIÓN</div>
    <div style="font-size:11px; color:#FDA4AF; margin-top:5px;">Viento: <b>{wind_speed} km/h</b> | Dir: <b>{wind_deg}°</b></div>
</div>
""", unsafe_allow_html=True)

def render_impact_alert(afectados):
    if not afectados: return ""
    html_lista = ""
    for item in afectados:
        icon = "bomb" if item['tipo'] == 'Gasolinera' else item['icon']
        html_lista += f'<div style="background:rgba(0,0,0,0.3); padding:8px; margin-bottom:5px; border-radius:4px; display:flex; align-items:center; gap:10px;"><i class="fa-solid fa-{icon}" style="color:{item["color"]}"></i><div><div style="font-weight:bold; font-size:12px;">{item["nombre"]}</div><div style="font-size:10px; color:#FECACA;">RIESGO INMINENTE</div></div></div>'
        
    return f"""
<div class="dash-card" style="border: 2px solid #EF4444; background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%); animation: pulse-red 2s infinite; margin-bottom: 20px;">
    <style>@keyframes pulse-red {{ 0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }} }}</style>
    <div style="color:white; font-weight:900; font-size:14px; margin-bottom:10px;"><i class="fa-solid fa-radiation"></i> IMPACTO CRÍTICO</div>
    <div style="margin-bottom:10px; font-size:12px; color:#FCA5A5;">{len(afectados)} infraestructuras en riesgo.</div>
    {html_lista}
</div>
"""