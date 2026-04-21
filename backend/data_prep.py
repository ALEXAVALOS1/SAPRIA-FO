import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 1. Definir rutas absolutas basadas en la estructura real de URBIPREX
# Esto asegura que siempre lea los archivos de public/data/
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "public", "data")

# Según las capturas del Director, estos son los nombres exactos de sus archivos reales:
ruta_manzanas = os.path.join(data_dir, "manzanas_datos.json")
ruta_incendios = os.path.join(data_dir, "incendios_reales.json")
ruta_bomberos = os.path.join(data_dir, "bomberos.json")

def cargar_json_a_gdf(ruta):
    """Función robusta que lee tanto GeoJSON de QGIS como JSONs planos exportados de Excel."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"⚠️ ERROR: No se encontró el archivo real en {ruta}")

    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Si el archivo es un GeoJSON nativo
    if isinstance(data, dict) and data.get('type') == 'FeatureCollection':
        return gpd.read_file(ruta)
        
    # Si el archivo es un JSON plano
    df = pd.DataFrame(data)
    cols = df.columns.str.lower()
    
    # Buscar dinámicamente las columnas de coordenadas
    real_lat = df.columns[cols.str.contains('lat|y')][0] if any(cols.str.contains('lat|y')) else None
    real_lon = df.columns[cols.str.contains('lon|lng|x')][0] if any(cols.str.contains('lon|lng|x')) else None
    
    if real_lat and real_lon:
        geometry = [Point(xy) for xy in zip(df[real_lon].astype(float), df[real_lat].astype(float))]
        return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    else:
        raise ValueError(f"⚠️ ERROR: No se detectaron columnas de coordenadas en {ruta}")

def preparar_datos():
    print("Iniciando motor de Ingeniería de Datos (100% Datos Reales)...")
    
    # PASO 1: Carga de datos
    print("1. Extrayendo datos desde public/data/...")
    gdf_manzanas = cargar_json_a_gdf(ruta_manzanas)
    gdf_incendios = cargar_json_a_gdf(ruta_incendios)
    gdf_bomberos = cargar_json_a_gdf(ruta_bomberos)

    # PASO 2: Reproyección a UTM Zona 13N (EPSG:32613) - Clave para Ciudad Juárez
    # Esto convierte los grados en METROS exactos para cálculos precisos.
    print("2. Reproyectando coordenadas al sistema métrico de Ciudad Juárez...")
    gdf_manzanas = gdf_manzanas.to_crs(epsg=32613)
    gdf_incendios = gdf_incendios.to_crs(epsg=32613)
    gdf_bomberos = gdf_bomberos.to_crs(epsg=32613)

    # Convertir polígonos a puntos centrales (centroides) para calcular radios
    centroides = gdf_manzanas.geometry.centroid

    # PASO 3: Calcular la Métrica Crítica (Densidad Espacial de Incendios)
    print("3. Calculando DENSIDAD ESPACIAL (Buscando incendios en radio de 500m por manzana)...")
    incendios_count = []
    for centroide in centroides:
        # Crea un radio táctico de 500 metros exactos
        buffer_500m = centroide.buffer(500)
        # Cuenta cuántos puntos reales del historial de incendios caen dentro de ese radio
        num_incendios = gdf_incendios.within(buffer_500m).sum()
        incendios_count.append(num_incendios)
        
    gdf_manzanas['densidad_incendios_500m'] = incendios_count

    # PASO 4: Calcular Distancia Numérica a Bomberos
    print("4. Calculando DISTANCIA A ESTACIONES DE BOMBEROS (En metros)...")
    distancias_bomberos = []
    for centroide in centroides:
        # Calcula la distancia a todas las estaciones y toma la menor
        distancia_minima = gdf_bomberos.distance(centroide).min()
        distancias_bomberos.append(distancia_minima)
        
    gdf_manzanas['distancia_bomberos_m'] = distancias_bomberos

    # PASO 5: Exportar la matriz matemática para el entrenamiento de la IA
    print("5. Ensamblando Dataset de Entrenamiento...")
    
    # Se elimina la columna 'geometry' porque la IA solo lee números, no formas espaciales
    dataset_final = pd.DataFrame(gdf_manzanas.drop(columns='geometry'))
    
    ruta_salida = os.path.join(base_dir, "backend", "dataset_entrenamiento.csv")
    dataset_final.to_csv(ruta_salida, index=False, encoding='utf-8')
    
    print("="*50)
    print(f"✅ ¡ÉXITO! Matriz de datos creada en: backend/dataset_entrenamiento.csv")
    print("Muestra de los nuevos cálculos reales:")
    print(dataset_final[['CVEGEO', 'densidad_incendios_500m', 'distancia_bomberos_m']].head())
    print("="*50)

if __name__ == "__main__":
    preparar_datos()