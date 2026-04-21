# URBIPREX: Sistema de Análisis Predictivo de Riesgos de Incendios Urbanos 🔥

![Status](https://img.shields.io/badge/Status-Activo-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**Sistema Municipal de Alertamiento Temprano para Ciudad Juárez.** Este proyecto utiliza Inteligencia Artificial, Big Data geoespacial y cruce masivo de bases de datos gubernamentales (INEGI) para identificar zonas de alto riesgo de incendio, optimizando la respuesta operativa y táctica de Protección Civil.

<div align="center">
  <img src="public/URBIPREX - LOGO GITHUB.PNG" alt="URBIPREX LOGO" width="400"/>
</div>

---

## 🎯 Objetivo
Desarrollar un modelo predictivo de grado institucional que genere mapas de riesgo manzana por manzana. El sistema evalúa infraestructura real, demografía, y variables climáticas dinámicas para predecir vulnerabilidades (como hacinamiento o densidad industrial) y apoyar la toma de decisiones preventivas.

## 🚀 Funcionalidades Principales
* **📡 Centro de Mando Táctico:** Interfaz frontend de baja latencia construida en React que permite a los operadores visualizar el riesgo de la ciudad mediante polígonos interactivos.
* **🤖 Cerebro Predictivo V4 (IA):** Modelo **Random Forest** entrenado con 7 variables críticas simultáneas: Distancia a bomberos, población, densidad vial, temperatura, viento, uso de suelo y riesgo eléctrico.
* **🗺️ Pipeline ETL Geoespacial:** Motor de extracción en Python que procesa e intersecta espacialmente decenas de miles de registros oficiales del Directorio Estadístico Nacional de Unidades Económicas (DENUE) y el Censo Poblacional (ITER).
* **🌤️ Simulador de Escenarios Estrés:** Módulo que permite inyectar condiciones climáticas extremas simuladas para prever el comportamiento del riesgo bajo presión térmica o ráfagas de viento.

## 🛠️ Stack Tecnológico
* **Frontend / UI:** React, TypeScript, Tailwind CSS
* **Backend / API:** FastAPI, Uvicorn, Python
* **Ingeniería de Datos (ETL):** GeoPandas, Pandas, Shapely
* **Machine Learning:** Scikit-learn, Joblib
* **Fuentes de Verdad (Datos):** INEGI (DENUE 2024, Censo ITER 2020), OpenWeatherMap

## 📂 Estructura del Proyecto
```text
URBIPREX/
├── backend/
│   ├── main.py                 # API de FastAPI (Puente de predicción)
│   ├── etl_geoespacial.py      # Motor ETL de cruce espacial (INEGI)
│   ├── train_model.py          # Script de entrenamiento IA (Random Forest)
│   └── modelo_urbiprex.pkl     # Cerebro V4 (Modelo exportado)
├── public/ 
│   ├── data/
│   │   └── manzanas_datos_produccion.json # Archivo Maestro GeoJSON
│   └── URBIPREX - LOGO GITHUB.PNG
├── src/ 
│   ├── components/
│   │   ├── MapView.tsx         # Renderizado del mapa táctico
│   │   ├── RightPanel.tsx      # Panel de telemetría y semáforos de riesgo
│   │   └── WeatherSimulator.tsx# Control de estrés climático
│   └── App.tsx                 # Ensamblaje del Centro de Mando
└── conjunto_de_datos/          # Archivos crudos del gobierno (CSV/SHP)