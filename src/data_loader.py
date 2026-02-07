import pandas as pd
import requests
import streamlit as st
from io import StringIO

# --- GESTIÓN DE CLAVES DE SEGURIDAD ---
try:
    # Intenta importar desde keys.py (Local)
    from src.keys import OPENWEATHER_KEY, NASA_KEY
except ImportError:
    # Si falla (Nube), intenta desde st.secrets
    try:
        OPENWEATHER_KEY = st.secrets["api_keys"]["openweather"]
        NASA_KEY = st.secrets["api_keys"]["nasa_firms"]
    except:
        OPENWEATHER_KEY = ""
        NASA_KEY = ""

def load_historical_data(csv_path):
    """
    Carga el CSV, renombra las columnas y limpia los datos.
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Mapeo de columnas
        column_mapping = {
            'Fecha': 'fecha',
            'Dirección (Cruces)': 'direccion',
            'Colonia / Sector': 'colonia',
            'Lat': 'lat',                 
            'Lon': 'lon',                 
            'Tipo de Incendio': 'tipo_incidente',
            'Causa Probable': 'causa',
            'Daños': 'dano',
            'Descripción / Contexto': 'descripcion',
            'Fuente': 'fuente'
        }
        
        # Renombrar
        df.rename(columns=column_mapping, inplace=True)

        # Limpieza
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        return df
    
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_weather_data(lat, lon):
    """Conecta con OpenWeatherMap"""
    try:
        if not OPENWEATHER_KEY:
            return None
            
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None