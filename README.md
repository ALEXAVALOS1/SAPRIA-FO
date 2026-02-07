# SAPRIA-FO: Sistema de Análisis Predictivo de Riesgos de Incendios Urbanos 🔥

![Status](https://img.shields.io/badge/Status-Activo-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Sistema Municipal de Alertamiento Temprano para Ciudad Juárez.**
Este proyecto utiliza Inteligencia Artificial y datos de fuentes abiertas para identificar zonas de alto riesgo de incendio, optimizando la respuesta de Protección Civil.

---

## 🎯 Objetivo
Desarrollar un modelo predictivo que genere mapas de calor de riesgo por manzana, utilizando datos históricos y variables climáticas en tiempo real para apoyar la toma de decisiones preventivas.

## 🚀 Funcionalidades Principales
* **📡 Monitoreo en Vivo:** Visualización geoespacial de incidentes históricos con mapas de calor (Heatmaps) nítidos y clusters interactivos.
* **🤖 Predicción IA:** Modelo **Random Forest** entrenado para predecir la probabilidad de incendios basándose en patrones espaciales y temporales.
* **🌤️ Clima en Tiempo Real:** Conexión vía API a OpenWeatherMap para monitorear condiciones detonantes (temperatura, viento, humedad).
* **📊 Dashboard Estadístico:** Métricas clave sobre las colonias con mayor incidencia y causas frecuentes.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.9+
* **Frontend/Dashboard:** Streamlit
* **Mapas:** Folium & Leaflet (CartoDB Dark Matter / Esri Satellite)
* **Ciencia de Datos:** Pandas, NumPy, Scikit-learn
* **APIs:** OpenWeatherMap, NASA FIRMS

## 📂 Estructura del Proyecto
```text
SAPRIA-FO/
├── src/
│   ├── data_loader.py    # Gestión de datos y conexión a APIs
│   ├── ai_model.py       # Lógica del modelo Random Forest
│   └── keys.py           # Credenciales (No incluido en repo por seguridad)
├── assets/               # Estilos CSS y recursos gráficos
├── app.py                # Punto de entrada de la aplicación
├── incendios.csv         # Dataset histórico (Anonimizado)
└── requirements.txt      # Dependencias