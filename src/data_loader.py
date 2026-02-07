import pandas as pd
import requests
import streamlit as st
from io import StringIO

# --- CAMBIO DE SEGURIDAD ---
# Intentamos importar desde el archivo privado keys.py
# Si no existe (ej. en la nube), buscamos en st.secrets
try:
    from src.keys import OPENWEATHER_KEY, NASA_KEY
except ImportError:
    # Plan B: Si estamos en la nube, usamos los secretos de Streamlit
    OPENWEATHER_KEY = st.secrets["api_keys"]["openweather"]
    NASA_KEY = st.secrets["api_keys"]["nasa_firms"]

# ... (El resto del código load_historical_data y get_weather_data sigue IGUAL)