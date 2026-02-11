import streamlit as st
from datetime import datetime, timedelta

def inject_tailwind():
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">', unsafe_allow_html=True)

def render_top_header_html():
    """Renderiza SOLO la fila superior (Logo y Links Institucionales)"""
    st.markdown("""
    <div style="background-color: #374151; padding: 15px 40px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="background-color: white; width: 35px; height: 35px; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                 <span class="material-icons-outlined" style="color: #374151; font-size: 24px;">shield</span>
            </div>
            <div style="height: 30px; width: 1px; background-color: rgba(255,255,255,0.2);"></div>
            <div style="line-height: 1.1;">
                <h1 style="color: #FACC15; font-weight: 800; font-size: 20px; margin: 0; letter-spacing: 0.5px;">SINAPRIA-FO</h1>
                <p style="color: white; font-size: 9px; font-weight: 600; margin: 0; letter-spacing: 1.5px; opacity: 0.8;">MONITOREO MUNICIPAL JUÁREZ</p>
            </div>
        </div>

        <div style="display: flex; align-items: center; gap: 25px;">
            <a href="#" style="color: white; text-decoration: none; font-size: 12px; font-weight: 600; opacity: 0.9;">Quiénes somos</a>
            <a href="#" style="color: white; text-decoration: none; font-size: 12px; font-weight: 600; opacity: 0.9;">Acciones Preventivas</a>
            <span class="material-icons-outlined" style="color: white; cursor: pointer;">search</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_left_alert_card(nasa_anomalies):
    if nasa_anomalies > 0:
        st.markdown(f"""
        <div class="bg-white rounded-xl p-4 shadow-sm border-l-4 border-red-500 mb-4">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-red-500 text-sm uppercase" style="margin:0;">Alerta Crítica Satelital</h3>
                <span class="animate-pulse h-2 w-2 rounded-full bg-red-500"></span>
            </div>
            <p class="text-xs text-gray-600 mb-2 font-medium">NASA VIIRS detectó {nasa_anomalies} anomalías térmicas.</p>
        </div>
        """, unsafe_allow_html=True)

def render_factors_card(weather, fwi_cat):
    temp = weather['main']['temp'] if weather else "--"
    hum = weather['main']['humidity'] if weather else "--"
    st.markdown(f"""
    <div class="bg-white rounded-xl shadow-sm p-4 border border-gray-100 mb-4">
        <h2 class="font-bold text-gray-800 flex items-center gap-2 text-xs uppercase tracking-wider mb-4 m-0">
            <span class="material-icons-outlined text-gray-700 text-sm">analytics</span> Factores Climáticos
        </h2>
        <div class="space-y-3">
            <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <span class="material-icons-outlined text-gray-400">device_thermostat</span>
                <div class="flex flex-col"><span class="text-xs font-bold text-gray-700">Temp</span><span class="text-[10px] text-gray-500">{temp}°C</span></div>
            </div>
            <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <span class="material-icons-outlined text-gray-400">water_drop</span>
                <div class="flex flex-col"><span class="text-xs font-bold text-gray-700">Humedad</span><span class="text-[10px] text-gray-500">{hum}%</span></div>
            </div>
             <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg border-l-2 border-gray-700">
                <span class="material-icons-outlined text-gray-400">speed</span>
                <div class="flex flex-col"><span class="text-xs font-bold text-gray-700">FWI</span><span class="text-[10px] font-bold text-red-500">{fwi_cat}</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_right_metrics(total_incendios):
    st.markdown(f"""
    <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 mb-4">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Métricas: Juárez</h2>
        <div class="grid grid-cols-2 gap-4">
            <div class="bg-red-50 p-3 rounded-lg border border-red-100">
                <div class="text-3xl font-bold text-red-500">{total_incendios}</div>
                <div class="text-[10px] font-bold text-gray-600 mt-1 uppercase">Total Focos</div>
            </div>
            <div class="bg-yellow-50 p-3 rounded-lg border border-yellow-100">
                <div class="text-3xl font-bold text-yellow-600">84%</div>
                <div class="text-[10px] font-bold text-gray-600 mt-1 uppercase">Vulnerabilidad</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_log_card(epicentros_ia):
    html = '<div class="bg-white rounded-xl shadow-sm border border-gray-100 flex-grow flex flex-col overflow-hidden mb-4">'
    html += '<div class="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">'
    html += '<h2 class="text-xs font-bold text-gray-800 uppercase tracking-wider m-0">Zonas K-Means (IA)</h2></div><div class="p-4 space-y-3">'
    if epicentros_ia:
        for ep in epicentros_ia[:3]:
            html += '<div class="p-3 rounded-lg border border-gray-100 bg-white"><div class="flex justify-between items-start mb-2">'
            html += f'<h4 class="text-xs font-bold text-gray-800 m-0">Epicentro {ep["id"]}</h4>'
            html += f'<span class="text-[9px] bg-red-500 text-white px-2 py-0.5 rounded font-black shadow-sm">{ep["peligro"]}</span>'
            html += '</div></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_forecast_section(base_temp):
    now = datetime.now()
    html = '<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mt-4">'
    html += '<div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4 flex justify-between"><span>Pronóstico (15h)</span><span>Live</span></div>'
    html += '<div class="flex justify-between items-center text-center">'
    for i in range(5):
        future_time = now + timedelta(hours=i*3)
        t_val = round(base_temp - (i*0.5)) 
        html += f'<div class="flex flex-col items-center"><span class="text-[10px] text-gray-500 font-bold mb-1">{future_time.strftime("%I %p")}</span>'
        html += f'<span class="text-sm font-black text-gray-800">{t_val}°</span></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_footer():
    st.markdown("""<footer class="bg-gray-800 text-white pt-10 pb-4 mt-8"><p class="text-center text-[10px] opacity-50">© 2026 SINAPRIA-FO</p></footer>""", unsafe_allow_html=True)