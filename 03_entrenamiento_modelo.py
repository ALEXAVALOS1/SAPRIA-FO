import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
import json
import os

print("🧠 Iniciando Fase 3 MAESTRA: El Ajuste Fino (Ratio 1:2)...")

ruta_csv = "data/outputs/dataset_final.csv"
if not os.path.exists(ruta_csv):
    print(f"❌ Error: No se encuentra {ruta_csv}.")
    exit()

df = pd.read_csv(ruta_csv)
df['ocurrio_incendio'] = (df['total_incendios'] > 0).astype(int)

print("🧬 Aplicando Ingeniería de Características...")
df['riesgo_pob_vial'] = df['densidad_pob'] * df['densidad_vial']
df['aislamiento_tactico'] = df['acceso_bomberos_km'] / (df['densidad_vial'] + 0.01)

caracteristicas = [
    'acceso_bomberos_km', 
    'densidad_vial', 
    'poblacion_total', 
    'densidad_pob', 
    'riesgo_pob_vial', 
    'aislamiento_tactico'
]

print("⚖️ Equilibrando la balanza al máximo (1 Incendio vs 2 Seguras)...")
df_incendios = df[df['ocurrio_incendio'] == 1]
df_seguras = df[df['ocurrio_incendio'] == 0]

# ⚠️ EL AJUSTE CLAVE: Ratio 1:2
muestras_seguras = len(df_incendios) * 2 
df_seguras_muestra = df_seguras.sample(n=muestras_seguras, random_state=42)

df_balanceado = pd.concat([df_incendios, df_seguras_muestra])

X_entrenamiento = df_balanceado[caracteristicas].fillna(0)
y_entrenamiento = df_balanceado['ocurrio_incendio']

# Escalamos
scaler = StandardScaler()
X_entrenamiento_scaled = scaler.fit_transform(X_entrenamiento)

# Tomamos un 25% para el examen final para tener una muestra más sólida
X_train, X_test, y_train, y_test = train_test_split(
    X_entrenamiento_scaled, y_entrenamiento, test_size=0.25, random_state=42, stratify=y_entrenamiento
)

print("⚙️ Entrenando Bosque Aleatorio de Alta Precisión...")
modelo = RandomForestClassifier(
    n_estimators=200,        # Suficientes árboles para votar
    max_depth=4,             # Poca profundidad para evitar que memorice
    min_samples_leaf=2,      # Regla estricta para formar ramas
    class_weight='balanced',
    random_state=42
)
modelo.fit(X_train, y_train)

print("\n🧮 EVALUANDO PREDICCIONES (EXAMEN FINAL DE LA IA):")
y_pred = modelo.predict(X_test)
y_prob = modelo.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)

print("-" * 40)
print(f"🎯 Métrica AUC-ROC: {auc:.3f} (Objetivo: >= 0.70)")
print("-" * 40)
print("\nReporte Detallado:\n", classification_report(y_test, y_pred))

print("\n🔍 Analizando la Importancia de Variables...")
importancias = modelo.feature_importances_

pesos_ia = {
    "Distancia_Bomberos": round(importancias[0] * 100, 1),
    "Densidad_Vial": round(importancias[1] * 100, 1),
    "Poblacion_Total": round(importancias[2] * 100, 1),
    "Densidad_Pob": round(importancias[3] * 100, 1),
    "Riesgo_Urbano": round(importancias[4] * 100, 1),
    "Aislamiento": round(importancias[5] * 100, 1)
}
print("Pesos Asignados:", pesos_ia)

print("\n🌐 Proyectando el aprendizaje a TODA Ciudad Juárez...")
# La IA aprendió las reglas con los 90 casos, ahora evaluará las 24,000 manzanas
X_total = df[caracteristicas].fillna(0)
X_total_scaled = scaler.transform(X_total)
df['ia_probabilidad_incendio'] = modelo.predict_proba(X_total_scaled)[:, 1]

os.makedirs("public/data", exist_ok=True)
with open("public/data/ia_pesos.json", "w") as f:
    json.dump(pesos_ia, f)

df.to_csv(ruta_csv, index=False)
print("✅ ¡Entrenamiento optimizado completado!")