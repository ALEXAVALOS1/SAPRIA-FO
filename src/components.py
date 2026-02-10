import streamlit as st

def inject_tailwind():
    """Inyecta la librería Tailwind CSS vía CDN para renderizar tu diseño."""
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">', unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <header class="bg-primary text-white shadow-md">
        <div class="container mx-auto px-4 py-3 flex justify-between items-center">
            <div class="flex items-center gap-4">
                <span class="material-icons-outlined text-secondary text-3xl">local_fire_department</span>
                <div class="border-l border-white/20 h-8 mx-2"></div>
                <div class="leading-tight">
                    <h1 class="font-bold text-xl text-secondary" style="margin:0;">SINAPRIA-FO</h1>
                    <p class="text-[10px] text-white/80 tracking-widest uppercase font-semibold" style="margin:0; font-size:10px;">MONITOREO MUNICIPAL JUÁREZ</p>
                </div>
            </div>
            <nav class="hidden md:flex items-center gap-6 text-sm font-semibold">
                <a class="hover:text-secondary transition-colors" style="color:white; text-decoration:none;" href="#">Quiénes somos</a>
                <a class="hover:text-secondary transition-colors" style="color:white; text-decoration:none;" href="#">Acciones Preventivas</a>
            </nav>
        </div>
    </header>
    <div class="bg-primary shadow-lg border-t border-white/5" style="border-top: 1px solid rgba(255,255,255,0.1);">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between h-12">
                <div class="flex items-center space-x-6 text-white/90 text-sm font-semibold">
                    <span class="text-secondary border-b-2 border-secondary pb-3 pt-3">Dashboard Principal</span>
                    <span class="hover:text-secondary pb-3 pt-3 transition-colors cursor-pointer">Reportes Históricos</span>
                    <span class="hover:text-secondary pb-3 pt-3 transition-colors cursor-pointer">Alertas Activas</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_left_alert_card(nasa_anomalies):
    if nasa_anomalies > 0:
        st.markdown(f"""
        <div class="bg-card-light rounded-xl p-4 shadow-sm border-l-4 border-alert-red mb-4">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-alert-red text-sm uppercase" style="margin:0;">Alerta Crítica Satelital</h3>
                <span class="animate-pulse h-2 w-2 rounded-full bg-alert-red"></span>
            </div>
            <p class="text-xs text-gray-600 mb-2 font-medium">NASA VIIRS detectó {nasa_anomalies} anomalías térmicas recientes.</p>
        </div>
        """, unsafe_allow_html=True)

def render_factors_card(weather, fwi_cat):
    temp = weather['main']['temp'] if weather else "--"
    hum = weather['main']['humidity'] if weather else "--"
    st.markdown(f"""
    <div class="bg-card-light rounded-xl shadow-sm p-4 border border-gray-100 mb-4">
        <div class="flex flex-col mb-4">
            <h2 class="font-bold text-gray-800 flex items-center gap-2 text-xs uppercase tracking-wider m-0">
                <span class="material-icons-outlined text-primary text-sm">analytics</span> Factores Climáticos
            </h2>
        </div>
        <div class="space-y-3">
            <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <span class="material-icons-outlined text-gray-500 bg-white p-1.5 rounded-md shadow-sm">device_thermostat</span>
                <div class="flex flex-col"><span class="text-xs font-bold text-gray-700">Temperatura</span><span class="text-[10px] text-gray-500">{temp}°C</span></div>
            </div>
            <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <span class="material-icons-outlined text-gray-500 bg-white p-1.5 rounded-md shadow-sm">water_drop</span>
                <div class="flex flex-col"><span class="text-xs font-bold text-gray-700">Humedad</span><span class="text-[10px] text-gray-500">{hum}%</span></div>
            </div>
            <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg border-l-2 border-primary">
                <span class="material-icons-outlined text-gray-500 bg-white p-1.5 rounded-md shadow-sm">speed</span>
                <div class="flex flex-col"><span class="text-xs font-bold text-gray-700">Riesgo FWI</span><span class="text-[10px] font-bold text-alert-red">{fwi_cat}</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_right_metrics(total_incendios):
    st.markdown(f"""
    <div class="bg-card-light rounded-xl p-5 shadow-sm border border-gray-100 mb-4">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Métricas: Juárez</h2>
        <div class="grid grid-cols-2 gap-4">
            <div class="bg-red-50 p-3 rounded-lg border border-red-100">
                <div class="text-3xl font-bold text-alert-red">{total_incendios}</div>
                <div class="text-[10px] font-bold text-gray-600 mt-1 uppercase">Total Focos</div>
            </div>
            <div class="bg-yellow-50 p-3 rounded-lg border border-yellow-100">
                <div class="text-3xl font-bold text-yellow-700">84%</div>
                <div class="text-[10px] font-bold text-gray-600 mt-1 uppercase">Vulnerabilidad</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_log_card(epicentros_ia):
    html = """
    <div class="bg-card-light rounded-xl shadow-sm border border-gray-100 flex-grow flex flex-col overflow-hidden mb-4">
        <div class="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
            <h2 class="text-xs font-bold text-gray-800 uppercase tracking-wider m-0">Zonas K-Means (IA)</h2>
        </div>
        <div class="p-4 space-y-3">
    """
    if epicentros_ia:
        for ep in epicentros_ia[:3]:
            badge_color = "bg-alert-red" if ep['peligro'] == "CRÍTICO" else "bg-secondary"
            html += f"""
            <div class="p-3 rounded-lg border border-gray-100 bg-white">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="text-xs font-bold text-gray-800 m-0">Epicentro {ep['id']}</h4>
                    <span class="text-[9px] {badge_color} text-white px-2 py-0.5 rounded font-black shadow-sm">{ep['peligro']}</span>
                </div>
                <p class="text-xs text-gray-500 mt-1 m-0">Concentración estadística: {ep['weight']} eventos históricos.</p>
            </div>
            """
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <footer class="bg-primary text-white pt-10 pb-4 mt-8">
        <div class="container mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8 text-sm mb-10">
            <div>
                <h2 class="text-2xl font-bold tracking-tighter text-secondary m-0">SINAPRIA-FO</h2>
                <p class="text-xs opacity-70 mt-1 max-w-[200px] font-medium">Sistema Municipal de Alertamiento Temprano para la Prevención de Incendios en Juárez.</p>
            </div>
            <div>
                <h5 class="font-bold mb-4 text-secondary uppercase tracking-widest text-xs">Emergencias 24/7</h5>
                <p class="text-4xl font-black text-white tracking-tighter m-0">911</p>
                <p class="text-[10px] opacity-70 font-bold leading-normal uppercase tracking-widest mt-2">Centro de Monitoreo SINAPRIA-FO. Ciudad Juárez, Chih.</p>
            </div>
        </div>
        <div class="container mx-auto px-4 pt-4 border-t border-white/10 text-center">
            <p class="text-[10px] opacity-50 font-bold tracking-widest uppercase m-0">© 2026 SINAPRIA-FO - Juárez Municipio</p>
        </div>
    </footer>
    """, unsafe_allow_html=True)



    # Forzando actualizacion para Streamlit
    