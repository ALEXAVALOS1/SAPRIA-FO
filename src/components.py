import streamlit as st
from datetime import datetime, timedelta

def inject_tailwind():
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">', unsafe_allow_html=True)

def render_left_alert_card(nasa_anomalies):
    if nasa_anomalies > 0:
        st.markdown(f'<div style="background:white;padding:1rem;border-radius:0.75rem;border-left:4px solid #EF4444;margin-bottom:1rem;box-shadow:0 1px 2px 0 rgba(0,0,0,0.05);"><div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;"><h3 style="color:#EF4444;font-weight:700;font-size:0.875rem;text-transform:uppercase;margin:0;">ALERTA CRÍTICA</h3><span style="height:0.5rem;width:0.5rem;background-color:#EF4444;border-radius:9999px;"></span></div><p style="color:#4B5563;font-size:0.75rem;font-weight:500;margin:0;">NASA VIIRS detectó {nasa_anomalies} anomalías.</p></div>', unsafe_allow_html=True)

def render_factors_card(weather, fwi_cat):
    t = weather['main']['temp'] if weather else "--"
    h = weather['main']['humidity'] if weather else "--"
    st.markdown(f'<div style="background:white;padding:1rem;border-radius:0.75rem;box-shadow:0 1px 2px 0 rgba(0,0,0,0.05);border:1px solid #F3F4F6;margin-bottom:1rem;"><h2 style="color:#1F2937;font-weight:700;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;"><span class="material-icons-outlined" style="font-size:1rem;color:#374151;">analytics</span>CLIMA EN VIVO</h2><div style="display:flex;flex-direction:column;gap:0.75rem;"><div style="display:flex;align-items:center;gap:0.75rem;padding:0.5rem;background-color:#F9FAFB;border-radius:0.5rem;"><span class="material-icons-outlined" style="color:#9CA3AF;">device_thermostat</span><div style="display:flex;flex-direction:column;"><span style="font-weight:700;font-size:0.75rem;color:#374151;">Temp</span><span style="font-size:0.65rem;color:#6B7280;">{t}°C</span></div></div><div style="display:flex;align-items:center;gap:0.75rem;padding:0.5rem;background-color:#F9FAFB;border-radius:0.5rem;border-left:2px solid #374151;"><span class="material-icons-outlined" style="color:#9CA3AF;">speed</span><div style="display:flex;flex-direction:column;"><span style="font-weight:700;font-size:0.75rem;color:#374151;">FWI</span><span style="font-size:0.65rem;font-weight:700;color:#EF4444;">{fwi_cat}</span></div></div></div></div>', unsafe_allow_html=True)

def render_right_metrics(total):
    st.markdown(f'<div style="background:white;padding:1.25rem;border-radius:0.75rem;box-shadow:0 1px 2px 0 rgba(0,0,0,0.05);border:1px solid #F3F4F6;margin-bottom:1rem;"><h2 style="color:#6B7280;font-weight:700;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">MÉTRICAS</h2><div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;"><div style="background-color:#FEF2F2;padding:0.75rem;border-radius:0.5rem;border:1px solid #FEE2E2;"><div style="font-size:1.875rem;font-weight:700;color:#EF4444;">{total}</div><div style="font-size:0.65rem;font-weight:700;color:#4B5563;text-transform:uppercase;margin-top:0.25rem;">FOCOS</div></div><div style="background-color:#FEFCE8;padding:0.75rem;border-radius:0.5rem;border:1px solid #FEF9C3;"><div style="font-size:1.875rem;font-weight:700;color:#CA8A04;">84%</div><div style="font-size:0.65rem;font-weight:700;color:#4B5563;text-transform:uppercase;margin-top:0.25rem;">RIESGO</div></div></div></div>', unsafe_allow_html=True)

def render_log_card(epicentros_ia):
    content = ""
    if epicentros_ia:
        for ep in epicentros_ia[:3]:
            content += f'<div style="padding:0.75rem;border-radius:0.5rem;border:1px solid #F3F4F6;background-color:white;"><div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;"><h4 style="font-size:0.75rem;font-weight:700;color:#1F2937;margin:0;">ZONA {ep["id"]}</h4><span style="font-size:0.6rem;background-color:#EF4444;color:white;padding:0.125rem 0.5rem;border-radius:0.25rem;font-weight:900;">{ep["peligro"]}</span></div></div>'
    st.markdown(f'<div style="background:white;border-radius:0.75rem;box-shadow:0 1px 2px 0 rgba(0,0,0,0.05);border:1px solid #F3F4F6;margin-bottom:1rem;overflow:hidden;"><div style="padding:1rem;border-bottom:1px solid #F3F4F6;background-color:#F9FAFB;"><h2 style="font-size:0.75rem;font-weight:700;color:#1F2937;text-transform:uppercase;letter-spacing:0.05em;margin:0;">ZONAS IA</h2></div><div style="padding:1rem;display:flex;flex-direction:column;gap:0.75rem;">{content}</div></div>', unsafe_allow_html=True)

def render_forecast_section(base_temp):
    items = ""
    now = datetime.now()
    for i in range(5):
        ft = now + timedelta(hours=i*3)
        val = round(base_temp - (i*0.5))
        items += f'<div style="display:flex;flex-direction:column;align-items:center;"><span style="font-size:0.65rem;color:#6B7280;font-weight:700;margin-bottom:0.25rem;">{ft.strftime("%I %p")}</span><span style="font-size:0.875rem;font-weight:900;color:#1F2937;">{val}°</span></div>'
    st.markdown(f'<div style="background:white;border-radius:0.75rem;box-shadow:0 1px 2px 0 rgba(0,0,0,0.05);border:1px solid #F3F4F6;padding:1.25rem;margin-top:1rem;"><div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;display:flex;justify-content:space-between;"><span>PRONÓSTICO</span><span>LIVE</span></div><div style="display:flex;justify-content:space-between;align-items:center;text-align:center;">{items}</div></div>', unsafe_allow_html=True)

def render_footer():
    st.markdown('<footer style="background-color:#1F2937;color:white;padding-top:2.5rem;padding-bottom:1rem;margin-top:2rem;"><p style="text-align:center;font-size:0.65rem;opacity:0.5;">© 2026 SAPRIA-FO</p></footer>', unsafe_allow_html=True)