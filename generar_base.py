import os
import osmnx as ox
import pandas as pd
import geopandas as gpd
import requests

# 1. Configuración del Área de Estudio
# Usamos el nombre del municipio tal como está en OpenStreetMap
place_name = "Juárez, Chihuahua, México"

print(f"🚀 Iniciando descarga de Red Vial...")
print("⏳ Esto puede tomar un par de minutos dependiendo de tu conexión a internet...")

# Intentamos descargar la red vial con manejo de errores
try:
    print(f"Buscando fronteras para: {place_name}...")
    graph = ox.graph_from_place(place_name, network_type='drive')
    print("✅ Red vial descargada por fronteras del municipio.")
    
except Exception as e:
    # PLAN B INFALIBLE: Si falla la búsqueda por nombre, usamos coordenadas y un radio
    print("⚠️ OSM no devolvió un polígono exacto. Activando Plan B (Coordenadas y Radio)...")
    # Coordenadas centrales de Ciudad Juárez
    centro_juarez = (31.7333, -106.4833) 
    # Descargamos 15 km a la redonda (cubre perfectamente la mancha urbana)
    graph = ox.graph_from_point(centro_juarez, dist=15000, network_type='drive')
    print("✅ Red vial urbana descargada exitosamente por radio de coordenadas.")

# 2. Obtener datos de Altitud
print("⛰️ Procesando datos de altitud...")
try:
    print("⚠️ Nota: Elevación mediante API omitida temporalmente (presupuesto $0). Se continuará con geometría 2D.")
except Exception as e:
    print(f"⚠️ Error en altitud: {e}")

# 3. Convertir a GeoDataFrame (Formato Espacial)
print("🗺️ Convirtiendo a formato espacial (GeoDataFrame)...")
nodes, edges = ox.graph_to_gdfs(graph)

# 4. Guardar como Dataset Base (GeoPackage) en la estructura correcta del proyecto
os.makedirs('data/processed', exist_ok=True)
os.makedirs('public/data', exist_ok=True)

print("💾 Guardando Dataset Espacial Base para Entrenamiento IA...")
ruta_gpkg = "data/processed/red_vial_juarez.gpkg"
edges.to_file(ruta_gpkg, layer='calles', driver="GPKG")
nodes.to_file(ruta_gpkg, layer='nodos', driver="GPKG")

# 5. Exportar una versión ligera para tu Mapa Web (React / Leaflet)
print("🌐 Generando versión ligera para el dashboard web...")
# Filtramos solo las vías principales para que el navegador web no colapse
calles_principales = edges[edges['highway'].isin(['primary', 'secondary', 'tertiary', 'trunk', 'motorway'])]

# Aseguramos que el sistema de coordenadas sea compatible con Leaflet (WGS84)
calles_principales = calles_principales.to_crs(epsg=4326)

# Guardamos el JSON ligero en la carpeta pública de React
ruta_json = "public/data/red_vial.json"
calles_principales.to_file(ruta_json, driver='GeoJSON')

print("✅ ¡Proceso completado con éxito!")
print(f"📁 Archivos generados en:\n - {ruta_gpkg} (Base de datos IA)\n - {ruta_json} (Visualización React)")