import streamlit as st
from datetime import datetime, timedelta

def inject_tailwind():
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">', unsafe_allow_html=True)

def render_left_alert_card(nasa_anomalies):
    if nasa_anomalies > 0:
        html = f'<div style="background:white;padding:1rem;border-radius:0.75rem;border-left:4px solid #EF4444;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);"><div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.5rem;"><h3 style="color:#EF4444;font-weight:700;font-size:0.875rem;margin:0;">ALERTA CRÍTICA</h3><span style="height:8px;width:8px;background:#EF4444;border-radius:50%;"></span></div><p style="color:#4B5563;font-size:0.75rem;margin:0;">NASA VIIRS detectó {nasa_anomalies} anomalías.</p></div>'
        st.markdown(html, unsafe_allow_html=True)

def render_factors_card(weather, fwi_cat):
    # DATOS
    temp = f"{weather['main']['temp']}°C" if weather else "--"
    wind = f"{weather['wind']['speed'] * 3.6:.1f} km/h" if weather else "--"
    w_deg = weather['wind']['deg'] if weather else 0
    # HTML COMPACTO (Copiado exactamente así funciona)
    html = f"""<div style="background:white;padding:1rem;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin-bottom:1rem;"><h2 style="color:#1F2937;font-size:12px;font-weight:bold;margin-bottom:10px;display:flex;align-items:center;gap:5px;"><span class="material-icons-outlined" style="font-size:16px;">analytics</span>CLIMA TÁCTICO</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;"><div style="background:#F9FAFB;padding:8px;border-radius:8px;display:flex;align-items:center;gap:8px;"><span class="material-icons-outlined" style="color:#9CA3AF;">device_thermostat</span><div><span style="font-size:10px;color:#6B7280;font-weight:bold;display:block;">TEMP</span><span style="font-size:14px;color:#1F2937;font-weight:bold;">{temp}</span></div></div><div style="background:#F9FAFB;padding:8px;border-radius:8px;display:flex;align-items:center;gap:8px;border-left:2px solid #EF4444;"><span class="material-icons-outlined" style="color:#EF4444;">local_fire_department</span><div><span style="font-size:10px;color:#6B7280;font-weight:bold;display:block;">FWI</span><span style="font-size:12px;color:#EF4444;font-weight:bold;">{fwi_cat}</span></div></div><div style="background:#F9FAFB;padding:8px;border-radius:8px;display:flex;align-items:center;gap:8px;"><span class="material-icons-outlined" style="color:#9CA3AF;">air</span><div><span style="font-size:10px;color:#6B7280;font-weight:bold;display:block;">VIENTO</span><span style="font-size:14px;color:#1F2937;font-weight:bold;">{wind}</span></div></div><div style="background:#F9FAFB;padding:8px;border-radius:8px;display:flex;align-items:center;gap:8px;"><span class="material-icons-outlined" style="color:#FACC15;transform:rotate({w_deg}deg);">navigation</span><div><span style="font-size:10px;color:#6B7280;font-weight:bold;display:block;">DIR</span><span style="font-size:14px;color:#1F2937;font-weight:bold;">{w_deg}°</span></div></div></div></div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_right_metrics(total):
    html = f'<div style="background:white;padding:1.25rem;border-radius:0.75rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin-bottom:1rem;"><h2 style="font-size:0.75rem;font-weight:700;color:#6B7280;margin-bottom:1rem;">MÉTRICAS</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;"><div style="background:#FEF2F2;padding:0.75rem;border-radius:0.5rem;border:1px solid #FEE2E2;"><div style="font-size:1.8rem;font-weight:700;color:#EF4444;">{total}</div><div style="font-size:0.65rem;font-weight:700;color:#4B5563;">FOCOS</div></div><div style="background:#FEFCE8;padding:0.75rem;border-radius:0.5rem;border:1px solid #FEF9C3;"><div style="font-size:1.8rem;font-weight:700;color:#CA8A04;">84%</div><div style="font-size:0.65rem;font-weight:700;color:#4B5563;">RIESGO</div></div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_log_card(epicentros_ia):
    content = ""
    if epicentros_ia:
        for ep in epicentros_ia[:3]:
            content += f'<div style="padding:0.75rem;background:white;border:1px solid #F3F4F6;border-radius:0.5rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;"><span style="font-size:0.75rem;font-weight:700;">Zona {ep["id"]}</span><span style="background:#EF4444;color:white;font-size:0.6rem;padding:2px 6px;border-radius:4px;font-weight:700;">{ep["peligro"]}</span></div>'
    html = f'<div style="background:white;border-radius:0.75rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);padding:1rem;margin-bottom:1rem;"><h2 style="font-size:0.75rem;font-weight:700;color:#1F2937;margin-bottom:1rem;">ZONAS IA</h2>{content}</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_forecast_section(base_temp):
    items = ""
    now = datetime.now()
    for i in range(5):
        ft = now + timedelta(hours=i*3)
        val = round(base_temp - (i*0.5))
        items += f'<div style="text-align:center;"><div style="font-size:0.65rem;color:#6B7280;font-weight:700;margin-bottom:2px;">{ft.strftime("%I %p")}</div><div style="font-size:0.9rem;font-weight:800;color:#1F2937;">{val}°</div></div>'
    html = f'<div style="background:white;border-radius:0.75rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);padding:1rem;margin-top:1rem;"><div style="display:flex;justify-content:space-between;margin-bottom:1rem;"><span style="font-size:0.65rem;font-weight:700;color:#9CA3AF;">PRONÓSTICO</span><span style="font-size:0.65rem;font-weight:700;color:#9CA3AF;">LIVE</span></div><div style="display:flex;justify-content:space-between;">{items}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_footer():
    st.markdown('<div style="text-align:center;padding:2rem;margin-top:2rem;color:#9CA3AF;font-size:0.75rem;">© 2026 SAPRIA-FO</div>', unsafe_allow_html=True)