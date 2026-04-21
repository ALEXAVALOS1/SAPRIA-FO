import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "backend", "dataset_entrenamiento.csv")
model_path = os.path.join(base_dir, "backend", "modelo_URBIPREX.pkl")

def entrenar_modelo_dinamico_v4():
    print("Iniciando actualización del modelo Random Forest (Cerebro V4 - Hacinamiento)...")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"⚠️ ERROR: No se encontró el dataset en {csv_path}")
        
    df = pd.read_csv(csv_path)
    df['target_riesgo'] = (df['densidad_incendios_500m'] > 0).astype(int)
    
    # --- FACTOR 1: CLIMA ---
    np.random.seed(42)
    df['temp'] = np.where(df['target_riesgo'] == 1, np.random.normal(38, 5, len(df)), np.random.normal(25, 8, len(df)))
    df['viento'] = np.where(df['target_riesgo'] == 1, np.random.normal(30, 10, len(df)), np.random.normal(15, 8, len(df)))
    df['temp'] = df['temp'].clip(10, 50)
    df['viento'] = df['viento'].clip(0, 80)

    # --- FACTOR 2: USO DE SUELO ---
    condiciones = [
        (df['poblacion_total'] <= 10) & (df['densidad_vial'] <= 20),
        (df['poblacion_total'] > 10),
        (df['poblacion_total'] <= 10) & (df['densidad_vial'] > 20)
    ]
    df['tipo_zona_calculada'] = np.select(condiciones, [1, 2, 3], default=1)

    # --- FACTOR 3: RIESGO ELÉCTRICO / HACINAMIENTO (NUEVO NUTRIENTE) ---
    # Le enseñamos a la IA que a mayor hacinamiento (más de 2 personas por cuarto), mayor riesgo de incendio
    df['PRO_OCUP_C'] = np.where(df['target_riesgo'] == 1, np.random.normal(2.5, 0.8, len(df)), np.random.normal(1.0, 0.4, len(df)))
    df['PRO_OCUP_C'] = df['PRO_OCUP_C'].clip(0.5, 5.0)

    # Definir variables predictoras actualizadas
    features = ['distancia_bomberos_m', 'poblacion_total', 'densidad_vial', 'temp', 'viento', 'tipo_zona_calculada', 'PRO_OCUP_C']
    print(f"Variables tácticas seleccionadas: {features}")
    
    X = df[features].fillna(0)
    y = df['target_riesgo']
    
    print("Entrenando la IA con las 7 variables maestras...")
    modelo = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    modelo.fit(X, y)
    
    joblib.dump(modelo, model_path)
    print("✅ ¡ÉXITO! Cerebro V4 (Producción Final) guardado.")

if __name__ == "__main__":
    entrenar_modelo_dinamico_v4()