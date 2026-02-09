import streamlit as st

def render_top_navbar():
    """Renderiza la barra de navegación superior falsa (estilo Dashboard profesional)."""
    st.markdown(f"""
    <div class="top-navbar">
        <div class="nav-left">
            <i class="fa-solid fa-shield-halved" style="color: #E11D48;"></i>
            SAPRIA-FO Monitor Municipal Juárez
        </div>
        <div class="nav-right">
            <span class="nav-item active">Dashboard</span>
            <span class="nav-item">Reportes</span>
            <span class="nav-item">Alertas</span>
            <span class="nav-item"><i class="fa-solid fa-user-circle"></i> Admin</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_card(nivel, descripcion):
    """
    Renderiza la tarjeta grande de Nivel de Riesgo (FWI).
    Cambia de color e icono según el nivel.
    """
    # Definir estilos según el nivel de riesgo
    color = "#10B981" # Verde (BAJO)
    icon = "fa-shield"
    
    if nivel == "MODERADO":
        color = "#3B82F6" # Azul
        icon = "fa-circle-check"
    elif nivel == "ALTO": 
        color = "#F59E0B" # Naranja
        icon = "fa-triangle-exclamation"
    elif nivel in ["MUY ALTO", "EXTREMO"]: 
        color = "#EF4444" # Rojo
        icon = "fa-fire"

    return f"""
    <div class="dash-card risk-card-large">
        <div class="risk-title-sm"><i class="fa-solid fa-circle-info"></i> NIVEL DE RIESGO</div>
        <div class="risk-status-large" style="color: {color};">
            <i class="fa-solid {icon}"></i> {nivel}
        </div>
        <div class="risk-subtext">{descripcion}</div>
    </div>
    """

def render_small_stat(titulo, valor, icono, color):
    """Renderiza tarjetas pequeñas de estadísticas (Temp, Humedad, Viento)."""
    return f"""
    <div class="small-stat-card" style="margin-top: 15px;">
        <i class="fa-solid {icono} stat-icon" style="color:{color};"></i>
        <div>
            <div class="stat-label">{titulo}</div>
            <div class="stat-value">{valor}</div>
        </div>
    </div>
    """

def render_map_floating_card(focos_activos, zona_critica):
    """
    Renderiza la tarjeta flotante blanca que aparece SOBRE el mapa.
    Muestra datos resumen del estado operativo.
    """
    return f"""
    <div style="position: relative; height: 0;">
        <div class="floating-map-card">
            <div class="fmc-header"><i class="fa-solid fa-fire"></i> ESTATUS TÁCTICO</div>
            <div class="fmc-body">
                <div class="fmc-row"><span>Focos Históricos:</span> <span class="fmc-val" style="color:#E11D48;">{focos_activos}</span></div>
                <div class="fmc-row"><span>Zona Caliente:</span> <span class="fmc-val">{str(zona_critica)[:15]}...</span></div>
                <div class="fmc-row"><span>Unidades:</span> <span class="fmc-val">3 Desplegadas</span></div>
            </div>
        </div>
    </div>
    """

def render_air_quality_card(aqi_data):
    """
    Renderiza la tarjeta de Calidad del Aire con barra de progreso.
    """
    if not aqi_data:
        return ""
        
    return f"""
    <div class="dash-card" style="margin-top: 15px;">
        <div style="font-size:12px; color:#9CA3AF; margin-bottom:10px; font-weight:bold;">
            <i class="fa-solid fa-wind"></i> CALIDAD DEL AIRE (AQI)
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <div style="font-size:24px; font-weight:800; color:{aqi_data['color']};">
                {aqi_data['texto']}
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; color:#9CA3AF;">PM2.5: {aqi_data['pm2_5']}</div>
                <div style="font-size:10px; color:#9CA3AF;">PM10: {aqi_data['pm10']}</div>
            </div>
        </div>
        <div style="margin-top:10px; height:4px; background:#1E293B; border-radius:2px;">
            <div style="width:{min(aqi_data['aqi']*20, 100)}%; height:100%; background:{aqi_data['color']}; border-radius:2px;"></div>
        </div>
    </div>
    """

def render_tactical_card(route_data, station_name):
    """
    Renderiza la tarjeta de Logística (Ruta activa).
    Solo se muestra cuando hay una ruta calculada.
    """
    if not route_data: return ""
    
    # Color dinámico según tiempo de respuesta
    color_time = "#10B981" # Verde (Rápido)
    if route_data['duration'] > 10: color_time = "#F59E0B" # Amarillo
    if route_data['duration'] > 20: color_time = "#EF4444" # Rojo
    
    return f"""
    <div class="dash-card" style="border: 1px solid #3B82F6; background: rgba(59, 130, 246, 0.05);">
        <div style="font-size:12px; color:#3B82F6; margin-bottom:10px; font-weight:bold; letter-spacing:1px;">
            <i class="fa-solid fa-route"></i> LOGÍSTICA DE RESPUESTA
        </div>
        <div style="display:flex; justify-content:space-between; align-items:end;">
            <div>
                <div style="font-size:11px; color:#9CA3AF;">UNIDAD ASIGNADA</div>
                <div style="font-size:14px; color:#FFFFFF; font-weight:600;">{station_name}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:28px; font-weight:900; color:{color_time}; line-height:1;">
                    {route_data['duration']}<span style="font-size:14px;"> min</span>
                </div>
                <div style="font-size:11px; color:#9CA3AF;">Distancia: {route_data['distance']} km</div>
            </div>
        </div>
    </div>
    """

def render_simulation_controls(wind_speed, wind_deg):
    """
    Muestra el panel informativo cuando el Modo Simulación está activo.
    """
    st.markdown("""
    <div style="background:#450a0a; padding:10px; border-radius:8px; border:1px solid #DC2626; margin-bottom:15px;">
        <div style="font-size:12px; color:#FCA5A5; font-weight:bold; margin-bottom:5px;">
            <i class="fa-solid fa-wind"></i> MODELO DE PROPAGACIÓN
        </div>
        <div style="font-size:11px; color:#FECACA;">
            Simulación basada en viento real. Proyección a 1 hora.
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:12px; color:white;">
            <span>Velocidad: <b>{} km/h</b></span>
            <span>Dirección: <b>{}°</b></span>
        </div>
    </div>
    """.format(wind_speed, wind_deg), unsafe_allow_html=True)

def render_impact_alert(afectados):
    """
    Renderiza la ALERTA ROJA PARPADEANTE cuando la simulación detecta
    que el fuego tocará una infraestructura crítica.
    """
    if not afectados:
        return ""
    
    html_lista = ""
    # Generar lista de infraestructuras afectadas
    for item in afectados:
        icon = item['icon']
        if item['tipo'] == 'Gasolinera': icon = "bomb" # Icono más dramático para combustible
        
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
    <div class="dash-card" style="border: 2px solid #EF4444; background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%); animation: pulse-red 2s infinite;">
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
            <button style="background:white; color:#DC2626; border:none; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:11px; cursor:pointer;">
                <i class="fa-solid fa-bullhorn"></i> INICIAR EVACUACIÓN
            </button>
        </div>
    </div>
    """