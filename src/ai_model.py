import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import streamlit as st

def train_fire_model(df):
    """
    Entrena un modelo Random Forest usando tus datos reales.
    Genera puntos de 'no-incendio' para balancear el aprendizaje.
    """
    if df.empty:
        return None, 0

    # 1. PREPARAR DATOS POSITIVOS (Tus incendios reales)
    # Extraemos características numéricas útiles
    df['month'] = df['fecha'].dt.month
    df['day_of_week'] = df['fecha'].dt.dayofweek
    
    # Variables de entrada (Features)
    X_pos = df[['lat', 'lon', 'month', 'day_of_week']].copy()
    y_pos = pd.Series([1] * len(X_pos)) # Etiqueta 1 = ¡Incendio!

    # 2. GENERAR DATOS NEGATIVOS (Background/Ausencia)
    # Esto es necesario para que la IA sepa distinguir zonas seguras
    # Generamos la misma cantidad de puntos aleatorios dentro de los límites de tus datos
    lat_min, lat_max = df['lat'].min(), df['lat'].max()
    lon_min, lon_max = df['lon'].min(), df['lon'].max()
    
    num_negatives = len(df)
    
    # Crear puntos aleatorios (simulación de zonas sin incidentes)
    neg_lats = np.random.uniform(lat_min, lat_max, num_negatives)
    neg_lons = np.random.uniform(lon_min, lon_max, num_negatives)
    neg_months = np.random.randint(1, 13, num_negatives)
    neg_days = np.random.randint(0, 7, num_negatives)
    
    X_neg = pd.DataFrame({
        'lat': neg_lats,
        'lon': neg_lons,
        'month': neg_months,
        'day_of_week': neg_days
    })
    y_neg = pd.Series([0] * len(X_neg)) # Etiqueta 0 = Seguro

    # 3. UNIR Y ENTRENAR
    X = pd.concat([X_pos, X_neg])
    y = pd.concat([y_pos, y_neg])
    
    # Dividir para validar (80% entrena, 20% examen)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # EL MODELO (Random Forest - Como pide el PDF)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluar precisión
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    return model, accuracy

def predict_risk_grid(model, lat_min, lat_max, lon_min, lon_max, current_date):
    """
    Genera una cuadrícula de predicción para visualizar el riesgo futuro
    """
    # Crear una malla de puntos sobre Juárez (Resolución 30x30)
    lat_range = np.linspace(lat_min, lat_max, 40)
    lon_range = np.linspace(lon_min, lon_max, 40)
    
    grid_points = []
    
    month = current_date.month
    day = current_date.weekday()
    
    for lat in lat_range:
        for lon in lon_range:
            grid_points.append({
                'lat': lat,
                'lon': lon,
                'month': month,
                'day_of_week': day
            })
            
    df_grid = pd.DataFrame(grid_points)
    
    # Predecir PROBABILIDAD (0 a 1)
    probs = model.predict_proba(df_grid)[:, 1] # Tomamos la probabilidad de clase 1 (Fuego)
    
    df_grid['risk_prob'] = probs
    return df_grid