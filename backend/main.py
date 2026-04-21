from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
from pydantic import BaseModel
import os
import json

# --- CONFIGURACIÓN DE RUTAS ---
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "modelo_URBIPREX.pkl")

# RUTA PARA GUARDAR REPORTES (Ajusta según tu estructura de carpetas)
# Normalmente: "../frontend/public/data/incendios_reales.json"
RUTA_DATOS = os.path.join(base_dir, "public", "data", "incendios_reales.json")

app = FastAPI(title="API Predictiva URBIPREX V4 (Producción + Captura)")

# --- CARGA DEL MODELO ---
modelo = joblib.load(model_path)

# --- CONFIGURACIÓN CORS ---
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- MODELOS DE DATOS ---
class DatosManzana(BaseModel):
    distancia_bomberos_m: float
    poblacion_total: float
    densidad_vial: float
    temp: float
    viento: float
    tipo_zona_calculada: int
    PRO_OCUP_C: float

class ReporteIncidente(BaseModel):
    lat: float
    lon: float
    tipo: str
    severidad: int
    notas: str
    fecha: str

# --- ENDPOINTS ---

@app.get("/")
def estado_servidor():
    return {"mensaje": "API URBIPREX V4 Operativa. Evaluando 7 factores tácticos + Receptor de Campo."}

@app.post("/predecir")
def calcular_riesgo(datos: DatosManzana):
    # Convertimos a DataFrame para el modelo .pkl
    df_entrada = pd.DataFrame([datos.dict()])
    orden_columnas = ['distancia_bomberos_m', 'poblacion_total', 'densidad_vial', 'temp', 'viento', 'tipo_zona_calculada', 'PRO_OCUP_C']
    df_entrada = df_entrada[orden_columnas]
    
    probabilidad = modelo.predict_proba(df_entrada)[0][1]
    
    return {
        "probabilidad_incendio": float(probabilidad),
        "porcentaje_visual": f"{round(probabilidad * 100, 2)}%"
    }

@app.post("/reportar")
async def recibir_reporte(reporte: ReporteIncidente):
    try:
        # 1. Leer historial existente
        if os.path.exists(RUTA_DATOS):
            with open(RUTA_DATOS, "r", encoding="utf-8") as file:
                datos_actuales = json.load(file)
        else:
            datos_actuales = []
            
        # 2. Crear nuevo registro
        nuevo = {
            "lat": reporte.lat,
            "lon": reporte.lon,
            "tipo": reporte.tipo,
            "fecha": reporte.fecha,
            "severidad": reporte.severidad,
            "notas": reporte.notas
        }
        
        datos_actuales.append(nuevo)
        
        # 3. Sobrescribir base de datos
        with open(RUTA_DATOS, "w", encoding="utf-8") as file:
            json.dump(datos_actuales, file, indent=4)
            
        return {"status": "ok", "mensaje": "Incidente registrado exitosamente."}
        
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}