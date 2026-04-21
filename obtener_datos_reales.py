import requests
import json
import os
import pandas as pd
import random

DATA_DIR = "public/data"

# ⚠️ ALERTA DE SEGURIDAD: Mantengo las API Keys para tu entorno local
NASA_KEY = "49510555e9a70b9a7c8ac71d1d01087a"
WEATHER_KEY = "60cbd579b9479b534ed3cd261e91bd9b"

def sync_juarez_real():
    print("🔄 Sincronizando datos para el dashboard de URBIPREX...")
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # 1. CLIMA ACTUAL (OpenWeather)
    print("⛅ Descargando clima actual...")
    try:
        w_url = f"https://api.openweathermap.org/data/2.5/weather?q=Ciudad%20Juarez,MX&units=metric&appid={WEATHER_KEY}"
        w_res = requests.get(w_url).json()
        clima = {
            "temp": w_res['main']['temp'],
            "humedad": w_res['main']['humidity'],
            "viento": round(w_res['wind']['speed'] * 3.6, 1),
            "desc": w_res['weather'][0]['description'].upper()
        }
        with open(f"{DATA_DIR}/clima_real.json", 'w', encoding='utf-8') as f: 
            json.dump(clima, f, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Error obteniendo clima: {e}")

    # 2. INCENDIOS HISTÓRICOS URBANOS (Tu CSV Real)
    print("🔥 Procesando incendios históricos urbanos desde CSV...")
    try:
        df_historico = pd.read_csv("incendios.csv")
        df_historico.columns = df_historico.columns.str.strip().str.lower()
        
        incendios_hist = []
        for _, r in df_historico.iterrows():
            incendios_hist.append({
                "lat": float(r['lat']),
                "lon": float(r['lon']),
                "fecha": str(r.get('fecha', 'N/D')),
                "tipo": str(r.get('tipo de incendio', 'Urbano')),
                "colonia": str(r.get('colonia / sector', 'N/D'))
            })
            
        print(f"✅ Se cargaron con éxito {len(incendios_hist)} incidentes históricos reales.")
        with open(f"{DATA_DIR}/incendios_reales.json", 'w', encoding='utf-8') as f: 
            json.dump(incendios_hist, f, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Error crítico leyendo incendios.csv: {e}")

    # 3. ESTACIONES BOMBEROS JUÁREZ (GPS Oficial Corregido)
    print("🚒 Actualizando estaciones de bomberos con ubicaciones reales...")
    bomberos = [
        {"nombre": "Estación Central (#1)", "lat": 31.7495, "lon": -106.4633, "dir": "Heroico Colegio Militar y 5 de Mayo"},
        {"nombre": "Estación No. 2", "lat": 31.7373, "lon": -106.4636, "dir": "Ignacio Ramírez y 16 de Septiembre"},
        {"nombre": "Estación No. 3", "lat": 31.7225, "lon": -106.4660, "dir": "Sanders y Sevilla"},
        {"nombre": "Estación No. 4", "lat": 31.6974, "lon": -106.3981, "dir": "Blvd. Gómez Morín y Faraday"},
        {"nombre": "Estación No. 7", "lat": 31.6481, "lon": -106.3811, "dir": "Henequén y Sonora (Salvárcar)"},
        {"nombre": "Estación No. 8", "lat": 31.6662, "lon": -106.4176, "dir": "Barranco Azul y Eje Vial"},
        {"nombre": "Estación No. 9", "lat": 31.7736, "lon": -106.5613, "dir": "C. Raya y Esturión (Anapra)"}
    ]
    with open(f"{DATA_DIR}/bomberos.json", 'w', encoding='utf-8') as f: 
        json.dump(bomberos, f, ensure_ascii=False)

    # 4. HIDRANTES (OSM Juárez)
    print("🚰 Consultando hidrantes en OpenStreetMap...")
    try:
        h_query = "[out:json];(node['emergency'='fire_hydrant'](31.55,-106.58,31.76,-106.30););out body;"
        h_res = requests.get("http://overpass-api.de/api/interpreter", params={'data': h_query}).json()
        hidrantes = [{"lat": e['lat'], "lon": e['lon']} for e in h_res['elements']]
        with open(f"{DATA_DIR}/hidrantes.json", 'w') as f: json.dump(hidrantes, f)
        print(f"✅ Se obtuvieron {len(hidrantes)} hidrantes.")
    except Exception as e:
        print(f"⚠️ Error obteniendo hidrantes: {e}")

    print(f"🚀 ¡TODOS LOS DATOS LISTOS PARA REACT!")

if __name__ == "__main__": 
    sync_juarez_real()