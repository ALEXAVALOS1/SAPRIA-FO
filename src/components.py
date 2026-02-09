import streamlit as st

# --- 1. COMPONENTES VISUALES (UI) ---

def render_top_navbar():
    """Renderiza la barra de navegación superior falsa."""
    st.markdown(f"""
    <div class="top-navbar">
        <div class="nav-brand">
            <i class="fa-solid fa-shield-halved" style="color: #E11D48; font-size: 20px;"></i>
            <span>SAPRIA-FO Monitor Municipal Juárez</span>
        </div>
        <div class="nav-links">
            <span class="nav-link active">Dashboard</span>
            <span class="nav-link">Reportes</span>
            <span class="nav-link">Alertas</span>
            <span class="nav-link">Prevención</span>
            <span class="nav-link">Ayuda</span>
        </div>
        <div class="nav-actions">
            <i class="fa-solid fa-magnifying-glass nav-link"></i>
            <i class="fa-solid fa-bell nav-link"></i>
            <i class="fa-solid fa-circle-user nav-link" style="font-size: 20px;"></i>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_map_floating_card(focos_activos, zona_critica):
    """Renderiza la tarjeta flotante sobre el mapa."""
    return f"""
    <div style="position: relative; height: 0; z-index: 1000;">
        <div class="floating-map-card">
            <div class="fmc-header">
                <i class="fa-solid fa-location-crosshairs"></i> ESTATUS TÁCTICO
            </div>
            <div class="fmc-body">
                <div class="fmc-row"><span>Focos Históricos:</span> <span class="fmc-val" style="color:#E11D48;">{focos_activos}</span></div>
                <div class="fmc-row"><span>Zona Caliente:</span> <span class="fmc-val">{str(zona_critica)[:18]}...</span></div>
                <div class="fmc-row"><span>Unidades:</span> <span class="fmc-val">3 Desplegadas</span></div>
            </div>
        </div>
    </div>
    """

def render_risk_card(nivel, descripcion):
    """Renderiza la tarjeta de Nivel de Riesgo (FWI) con colores dinámicos."""
    # Mapeo de colores e iconos
    colors = {
        "BAJO": ["#10B981", "fa-shield"],
        "MODERADO": ["#3B82F6", "fa-circle-check"],
        "ALTO": ["#F59E0B", "fa-triangle-exclamation"],
        "MUY ALTO": ["#F97316", "fa-fire"],
        "EXTREMO": ["#E11D48", "fa-fire-flame-curved"]
    }
    # Obtener valores o defaults
    color, icon = colors.get(nivel, ["#9CA3AF", "fa-question"])
    
    # Estilo del encabezado
    header_bg = color if nivel in ["ALTO", "MUY ALTO", "EXTREMO"] else "#1E293B" # Default oscuro
    header_text = "white" if nivel in ["ALTO", "MUY ALTO", "EXTREMO"] else "#94A3B8"

    return f"""
    <div class="dash-card" style="padding: 0; overflow: hidden; border:none; margin-bottom: 15px;">
        <div class="risk-card-header" style="background: {header_bg}; color: {header_text}; padding: 12px 20px; font-weight: 700; font-size: 12px; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid {icon}"></i> NIVEL DE RIESGO (FWI)
        </div>
        <div class="risk-card-body" style="background: #1E293B; padding: 20px; text-align: center;">
            <div class="risk-value" style="color: {color}; font-size: 32px; font-weight: 900;">{nivel}</div>
            <div class="risk-sub" style="font-size: 12px; color: #94A3B8;">{descripcion}</div>
        </div>
    </div>
    """

def render_small_stat(titulo, valor, icono, color, bg_icon_color):
    """Renderiza tarjetas pequeñas (Temperatura, Humedad)."""
    return f"""
    <div class="small-stat-card" style="margin-bottom: 15px;">
        <div class="stat-icon-box" style="background: {bg_icon_color}; color: {color};">
            <i class="fa-solid {icono}"></i>
        </div>
        <div>
            <div class="stat-label">{titulo}</div>
            <div class="stat-value">{valor}</div>
        </div>
    </div>
    """

def render_air_quality_card(aqi_data):
    """Renderiza la tarjeta de Calidad del Aire (AQI)."""
    if not aqi_data: return ""
    
    # Calcular porcentaje para la barra (max 100%)
    width_pct = min(aqi_data['aqi'] * 20, 100)
    
    return f"""
    <div class="dash-card" style="margin-bottom: 15px;">
        <div class="aqi-card-header" style="font-size: 12px; color: #94A3B8; font-weight: 700; margin-bottom: 15px;">
            <i class="fa-solid fa-wind"></i> CALIDAD DEL AIRE (AQI)
        </div>
        <div class="aqi-main" style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 10px;">
            <div class="aqi-status" style="color:{aqi_data['color']}; font-size: 28px; font-weight: 900;">{aqi_data['texto']}</div>
            <div class="aqi-details" style="text-align: right; font-size: 11px; color: #64748B;">
                <div>PM2.5: <b>{aqi_data['pm2_5']}</b></div>
                <div>PM10: <b>{aqi_data['pm10']}</b></div>
            </div>
        </div>
        <div class="aqi-bar-bg" style="height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px;">
            <div class="aqi-bar-fill" style="width:{width_pct}%; height:100%; background:{aqi_data['color']}; border-radius: 3px;"></div>
        </div>
    </div>
    """

def render_forecast_section():
    """
    Renderiza la barra de pronóstico horizontal.
    Retorna HTML STRING para ser usado con st.markdown(..., unsafe_allow_html=True)
    """
    # Datos simulados visualmente para mantener el diseño
    forecast_data = [
        {"time": "06:00 p.m.", "icon": "fa-cloud-sun", "temp": "19°", "pop": "19%", "badge": "BAJO", "color": "#10B981"},
        {"time": "09:00 p.m.", "icon": "fa-cloud-moon", "temp": "14°", "pop": "21%", "badge": "BAJO", "color": "#10B981"},
        {"time": "12:00 a.m.", "icon": "fa-moon", "temp": "9°", "pop": "22%", "badge": "BAJO", "color": "#10B981"},
        {"time": "03:00 a.m.", "icon": "fa-moon", "temp": "9°", "pop": "20%", "badge": "BAJO", "color": "#10B981"},
        {"time": "06:00 a.m.", "icon": "fa-cloud-sun", "temp": "9°", "pop": "30%", "badge": "MEDIO", "color": "#F59E0B"},
        {"time": "09:00 a.m.", "icon": "fa-sun", "temp": "14°", "pop": "10%", "badge": "BAJO", "color": "#10B981"},
    ]
    
    html_items = ""
    for item in forecast_data:
        icon_color = "#F59E0B" if "sun" in item['icon'] else "#3B82F6"
        html_items += f"""
        <div class="forecast-item">
            <div class="fc-time">{item['time']}</div>
            <i class="fa-solid {item['icon']} fc-icon" style="color:{icon_color};"></i>
            <div class="fc-temp">{item['temp']}</div>
            <div class="fc-pop"><i class="fa-solid fa-droplet"></i> {item['pop']}</div>
            <span class="fc-badge" style="background:{item['color']}20; color:{item['color']};">{item['badge']}</span>
        </div>
        """
        
    return f"""
    <div class="forecast-section">
        <div class="forecast-header">
            <span><i class="fa-regular fa-clock"></i> PRONÓSTICO DE RIESGO (PRÓXIMAS 12 HORAS)</span>
            <span style="font-size:10px; opacity:0.7;">Fuente: OpenWeatherMap Forecasting</span>
        </div>
        <div class="forecast-container">
            {html_items}
        </div>
    </div>
    """

# --- 2. FUNCIONES TÁCTICAS Y SIMULACIÓN (ESTAS FALTABAN) ---

def render_tactical_card(route_data, station_name):
    """Renderiza la tarjeta de Logística cuando hay ruta activa."""
    if not route_data: return ""
    
    color_time = "#10B981" # Verde
    if route_data['duration'] > 10: color_time = "#F59E0B" # Amarillo
    if route_data['duration'] > 20: color_time = "#EF4444" # Rojo
    
    return f"""
    <div class="dash-card" style="border: 1px solid #3B82F6; background: rgba(59, 130, 246, 0.05); margin-bottom: 15px;">
        <div style="font-size:12px; color:#3B82F6; margin-bottom:10px; font-weight:bold; letter-spacing:1px;">
            <i class="fa-solid fa-route"></i> LOGÍSTICA DE RESPUESTA
        </div>
        <div style="display:flex; justify-content:space-between; align-items:end;">
            <div>
                <div style="font-size:11px; color:#94A3B8;">UNIDAD ASIGNADA</div>
                <div style="font-size:14px; color:#FFFFFF; font-weight:600;">{station_name}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:28px; font-weight:900; color:{color_time}; line-height:1;">
                    {route_data['duration']}<span style="font-size:14px;"> min</span>
                </div>
                <div style="font-size:11px; color:#94A3B8;">Distancia: {route_data['distance']} km</div>
            </div>
        </div>
    </div>
    """

def render_simulation_controls(wind_speed, wind_deg):
    """Muestra el panel de control de simulación."""
    st.markdown("""
    <div style="background:rgba(225, 29, 72, 0.1); padding:15px; border-radius:12px; border:1px solid #E11D48; margin-bottom:15px;">
        <div style="font-size:12px; color:#E11D48; font-weight:bold; margin-bottom:5px;">
            <i class="fa-solid fa-wind"></i> MODELO DE PROPAGACIÓN
        </div>
        <div style="font-size:11px; color:#FDA4AF;">
            Simulación basada en viento real. Proyección a 1 hora.
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:12px; color:white;">
            <span>Velocidad: <b>{} km/h</b></span>
            <span>Dirección: <b>{}°</b></span>
        </div>
    </div>
    """.format(wind_speed, wind_deg), unsafe_allow_html=True)

def render_impact_alert(afectados):
    """Renderiza la ALERTA ROJA de impacto en infraestructura."""
    if not afectados: return ""
    
    html_lista = ""
    for item in afectados:
        icon = item['icon']
        if item['tipo'] == 'Gasolinera': icon = "bomb"
        
        html_lista += f"""
        <div style="background:rgba(0,0,0,0.3); padding:8px; margin-bottom:5px; border-radius:4px; display:flex; align-items:center; gap:10px;">
            <i class="fa-solid fa-{icon}" style="color:{item['color']}"></i>
            <div>
                <div style="font-weight:bold; font-size:12px;">{item['nombre']}</div>
                <div style="font-size:10px; color:#FECACA;">RIESGO INMINENTE</div>
            </div>
        </div>
        """

    return f"""
    <div class="dash-card" style="border: 2px solid #EF4444; background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%); animation: pulse-red 2s infinite; margin-bottom: 20px;">
        <style>
            @keyframes pulse-red {{
                0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
            }}
        </style>
        <div style="color:white; font-weight:900; font-size:14px; margin-bottom:10px; display:flex; align-items:center; gap:10px;">
            <i class="fa-solid fa-radiation"></i> ANÁLISIS DE IMPACTO CRÍTICO
        </div>
        <div style="margin-bottom:10px; font-size:12px; color:#FCA5A5;">
            La simulación indica que {len(afectados)} infraestructuras estratégicas están en la trayectoria directa del fuego.
        </div>
        {html_lista}
        <div style="margin-top:10px; text-align:center;">
            <button style="background:white; color:#DC2626; border:none; padding:8px 20px; border-radius:20px; font-weight:bold; font-size:11px; cursor:pointer;">
                <i class="fa-solid fa-bullhorn"></i> INICIAR EVACUACIÓN
            </button>
        </div>
    </div>
    """