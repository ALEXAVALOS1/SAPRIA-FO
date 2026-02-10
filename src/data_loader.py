import pandas as pd
import requests
import streamlit as st
from io import StringIO

# --- GESTIÓN DE CLAVES (OpenWeather / NASA) ---
try:
    from src.keys import OPENWEATHER_KEY, NASA_KEY
except ImportError:
    try:
        OPENWEATHER_KEY = st.secrets["api_keys"]["openweather"]
        NASA_KEY = st.secrets["api_keys"]["nasa_firms"]
    except:
        OPENWEATHER_KEY = ""
        NASA_KEY = ""

def load_historical_data(csv_path):
    """Carga el CSV real de incendios históricos."""
    try:
        df = pd.read_csv(csv_path)
        # Mapeo y limpieza estándar
        column_mapping = {
            'Fecha': 'fecha', 'Dirección (Cruces)': 'direccion', 'Colonia / Sector': 'colonia',
            'Lat': 'lat', 'Lon': 'lon', 'Tipo de Incendio': 'tipo_incidente',
            'Causa Probable': 'causa', 'Daños': 'dano', 'Descripción / Contexto': 'descripcion',
            'Fuente': 'fuente'
        }
        df.rename(columns=column_mapping, inplace=True)
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def get_weather_data(lat, lon):
    """Clima real desde OpenWeatherMap"""
    try:
        if not OPENWEATHER_KEY: return None
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
        response = requests.get(url, timeout=5)
        return response.json() if response.status_code == 200 else None
    except: return None

# --- NUEVO: INFRAESTRUCTURA REAL DESDE OPENSTREETMAP ---
@st.cache_data(ttl=3600) # Guardar en caché 1 hora para no saturar la API
def get_real_infrastructure(lat, lon, radius=8000):
    """
    Consulta la API de Overpass (OpenStreetMap) para obtener infraestructura REAL
    en un radio de 'radius' metros alrededor de las coordenadas.
    """
    api_url = "http://overpass-api.de/api/interpreter"
    
    # Consulta en lenguaje Overpass QL
    # Buscamos: Gasolineras (fuel), Escuelas (school), Bomberos (fire_station), Hospitales (hospital)
    query = f"""
    [out:json];
    (
      node["amenity"="fuel"](around:{radius},{lat},{lon});
      node["amenity"="school"](around:{radius},{lat},{lon});
      node["amenity"="fire_station"](around:{radius},{lat},{lon});
      node["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """
    
    try:
        response = requests.get(api_url, params={'data': query}, timeout=25)
        if response.status_code == 200:
            data = response.json().get('elements', [])
            
            processed_data = []
            for item in data:
                # Determinar tipo y asignar icono/color
                tag_amenity = item.get('tags', {}).get('amenity', 'unknown')
                name = item.get('tags', {}).get('name', 'Sin Nombre')
                
                if tag_amenity == 'fuel':
                    tipo = 'Gasolinera'
                    icon = 'gas-pump'
                    color = '#8B5CF6' # Morado
                elif tag_amenity == 'school':
                    tipo = 'Escuela'
                    icon = 'school'
                    color = '#3B82F6' # Azul
                elif tag_amenity == 'fire_station':
                    tipo = 'Bomberos'
                    icon = 'fire-extinguisher'
                    color = '#10B981' # Verde
                elif tag_amenity == 'hospital':
                    tipo = 'Hospital'
                    icon = 'hospital'
                    color = '#EF4444' # Rojo Cruz
                else:
                    continue
                
                processed_data.append({
                    "lat": item['lat'],
                    "lon": item['lon'],
                    "tipo": tipo,
                    "nombre": name,
                    "icon": icon,
                    "color": color
                })
            
            return pd.DataFrame(processed_data)
        else:
            return pd.DataFrame()
    except Exception as e:
        # Si falla (timeout), devolvemos vacío para no romper la app
        print(f"Error Overpass: {e}")
        return pd.DataFrame()

# --- AGREGAR AL FINAL DE src/data_loader.py ---

def get_air_quality(lat, lon):
    """Consulta la calidad del aire (AQI) en tiempo real."""
    try:
        if not OPENWEATHER_KEY: return None
        # Endpoint de contaminación del aire
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # OpenWeather devuelve: 1 (Bueno), 2 (Justo), 3 (Moderado), 4 (Pobre), 5 (Muy Pobre)
            aqi_val = data['list'][0]['main']['aqi']
            components = data['list'][0]['components'] # pm2_5, pm10, co, etc.
            
            # Traducir a texto
            niveles = {1: "BUENA", 2: "ACEPTABLE", 3: "MODERADA", 4: "MALA", 5: "PELIGROSA"}
            colores = {1: "#10B981", 2: "#F59E0B", 3: "#F97316", 4: "#EF4444", 5: "#7F1D1D"}
            
            return {
                "aqi": aqi_val,
                "texto": niveles.get(aqi_val, "Desconocido"),
                "color": colores.get(aqi_val, "#9CA3AF"),
                "pm2_5": components.get("pm2_5", 0),
                "pm10": components.get("pm10", 0)
            }
        return None
    except: return None

# --- AGREGAR AL FINAL DE src/data_loader.py ---

def get_route_osrm(start_lat, start_lon, end_lat, end_lon):
    """
    Obtiene la ruta óptima de manejo entre dos puntos usando OSRM (Gratis).
    Retorna: Geometría (lista de puntos), Duración (minutos), Distancia (km)
    """
    # OSRM usa formato lon,lat
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            route = data['routes'][0]
            
            # Extraer datos
            geometry = route['geometry']['coordinates'] # Ojo: OSRM devuelve [lon, lat]
            duration_min = round(route['duration'] / 60, 1)
            distance_km = round(route['distance'] / 1000, 2)
            
            # Convertir geometría a [lat, lon] para Folium
            lat_lon_path = [[pt[1], pt[0]] for pt in geometry]
            
            return {
                "path": lat_lon_path,
                "duration": duration_min,
                "distance": distance_km
            }
        return None
    except Exception as e:
        print(f"Error Routing: {e}")
        return None

def find_nearest_station(incident_lat, incident_lon, df_infra):
    """Encuentra la estación de bomberos más cercana de la lista de infraestructura."""
    if df_infra.empty: return None
    
    # Filtrar solo bomberos
    bomberos = df_infra[df_infra['tipo'] == 'Bomberos'].copy()
    if bomberos.empty: return None
    
    # Calcular distancia euclidiana simple para encontrar la más cercana
    # (Para mayor precisión usaríamos Haversine, pero esto basta para selección rápida)
    bomberos['dist'] = ((bomberos['lat'] - incident_lat)**2 + (bomberos['lon'] - incident_lon)**2)**0.5
    nearest = bomberos.sort_values('dist').iloc[0]
    
    return nearest

def get_nasa_firms_data():
    """
    Descarga el feed público de la NASA (FIRMS) de anomalías térmicas 
    detectadas por satélite en las últimas 24 horas (Centroamérica y México).
    """
    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Central_America_24h.csv"
    
    try:
        # Descargar el CSV en vivo desde los servidores de la NASA
        df_nasa = pd.read_csv(url)
        
        # Filtro de Bounding Box para la región de Ciudad Juárez / El Paso
        # Ampliamos un poco el margen para ver si hay incendios acercándose por el desierto
        lat_min, lat_max = 31.0, 32.2
        lon_min, lon_max = -107.0, -106.0
        
        df_filtered = df_nasa[
            (df_nasa['latitude'] >= lat_min) & (df_nasa['latitude'] <= lat_max) &
            (df_nasa['longitude'] >= lon_min) & (df_nasa['longitude'] <= lon_max)
        ]
        
        return df_filtered
    except Exception as e:
        print(f"Error de conexión con la NASA: {e}")
        return pd.DataFrame()
    # --- AGREGAR AL FINAL DE src/data_loader.py ---

def get_nasa_firms_data():
    """Descarga datos satelitales en vivo de la NASA (Anomalías térmicas 24h)."""
    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Central_America_24h.csv"
    try:
        df_nasa = pd.read_csv(url)
        # Filtrar solo el área de Ciudad Juárez / El Paso
        lat_min, lat_max = 31.0, 32.2
        lon_min, lon_max = -107.0, -106.0
        
        df_filtered = df_nasa[
            (df_nasa['latitude'] >= lat_min) & (df_nasa['latitude'] <= lat_max) &
            (df_nasa['longitude'] >= lon_min) & (df_nasa['longitude'] <= lon_max)
        ]
        return df_filtered
    except Exception as e:
        print(f"Error NASA: {e}")
        return pd.DataFrame()

        # --- AGREGAR AL FINAL DE src/data_loader.py ---
import requests
import math

def find_nearest_station(lat, lon, df_infra):
    """Encuentra la estación de bomberos más cercana a las coordenadas dadas."""
    bomberos = df_infra[df_infra['tipo'] == 'Bomberos'].copy()
    if bomberos.empty: return None
    
    # Cálculo de distancia básica (Pitágoras)
    bomberos['dist'] = ((bomberos['lat'] - lat)**2 + (bomberos['lon'] - lon)**2)**0.5
    nearest = bomberos.loc[bomberos['dist'].idxmin()]
    return nearest

def get_route_osrm(start_lat, start_lon, end_lat, end_lon):
    """Consulta al servidor OSRM para obtener la ruta por calles."""
    # OSRM pide primero Longitud y luego Latitud
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    try:
        res = requests.get(url).json()
        if res.get('code') == 'Ok':
            route = res['routes'][0]
            geometry = route['geometry']['coordinates']
            # Convertir [lon, lat] a [lat, lon] para Folium
            path = [[p[1], p[0]] for p in geometry]
            distance = round(route['distance'] / 1000, 2) # kilómetros
            duration = round(route['duration'] / 60) # minutos
            return {"path": path, "distance": distance, "duration": duration}
    except Exception as e:
        print(f"Error en ruteo: {e}")
    return None