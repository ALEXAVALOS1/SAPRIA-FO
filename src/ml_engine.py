from sklearn.cluster import KMeans
import pandas as pd

def get_risk_clusters(df, num_clusters=5):
    """
    Utiliza Inteligencia Artificial (K-Means Clustering) para encontrar 
    los epicentros matemáticos de riesgo basados en el historial.
    """
    if df.empty or len(df) < num_clusters:
        return []
    
    # Extraer solo las coordenadas válidas
    coords = df[['lat', 'lon']].dropna()
    
    # Entrenar el modelo de Machine Learning
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    kmeans.fit(coords)
    
    # Obtener los epicentros (centroides)
    centers = kmeans.cluster_centers_
    
    clusters = []
    for i, center in enumerate(centers):
        # Contar cuántos incidentes históricos "pertenecen" a este epicentro
        count = sum(kmeans.labels_ == i)
        clusters.append({
            "id": i + 1,
            "lat": center[0], 
            "lon": center[1], 
            "weight": count,
            "peligro": "CRÍTICO" if count > (len(df)/num_clusters)*1.2 else "ALTO"
        })
        
    # Ordenar del más peligroso al menos
    clusters = sorted(clusters, key=lambda x: x['weight'], reverse=True)
    return clusters

def generate_ai_briefing(weather, fwi_cat, anomalias_nasa, epicentros):
    """Genera un reporte de texto automatizado estilo militar."""
    temp = weather['main']['temp'] if weather else 0
    wind = weather['wind']['speed'] * 3.6 if weather else 0
    
    status = "ESTABLE"
    if fwi_cat in ["ALTO", "MUY ALTO", "EXTREMO"] or anomalias_nasa > 0:
        status = "CRÍTICO"
        
    html = f"""
    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-family: monospace; font-size: 11px; color: #38BDF8; line-height: 1.5;">
        <span style="color:#F1F5F9; font-weight:bold;">> INICIANDO DIAGNÓSTICO DEL SISTEMA...</span><br>
        > ESTADO GENERAL: <span style="color:{'#EF4444' if status=='CRÍTICO' else '#10B981'}; font-weight:bold;">{status}</span><br>
        > ANÁLISIS METEOROLÓGICO: Temp. {temp}°C | Viento {wind:.1f} km/h.<br>
        > RIESGO CALCULADO (FWI): Nivel {fwi_cat}.<br>
    """
    
    if anomalias_nasa > 0:
        html += f"> <span style="color:#EF4444; font-weight:bold;">¡ALERTA!</span> SATÉLITE VIIRS DETECTA {anomalias_nasa} ANOMALÍAS EN SECTOR.<br>"
    else:
        html += "> ESCANEO SATELITAL: Limpio. Sin firmas de calor activas.<br>"
        
    if epicentros:
        html += f"> PREDICCIÓN IA: El epicentro Alfa (Zona de mayor riesgo) concentra {epicentros[0]['weight']} incidentes previos. Mantener vigilancia."
        
    html += "</div>"
    return html