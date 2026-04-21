import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import json
import os

print("🚀 Iniciando Fase 2: Ingeniería de Características...")

# 1. Cargar las Manzanas (Base espacial)
print("🗺️ Cargando base de manzanas de Ciudad Juárez...")
ruta_gpkg = "data/processed/Dataset_Juarez_URBIPREX.gpkg"
manzanas = gpd.read_file(ruta_gpkg, layer='manzanas')

# 2. Cargar los Incendios y convertirlos en puntos espaciales
print("🔥 Procesando ubicaciones de incendios históricos...")
with open("public/data/incendios_reales.json", 'r', encoding='utf-8') as f:
    datos_incendios = json.load(f)

# Convertimos el JSON a un DataFrame de Pandas, y luego a GeoDataFrame
df_incendios = pd.DataFrame(datos_incendios)
geometria_incendios = [Point(xy) for xy in zip(df_incendios['lon'], df_incendios['lat'])]
# EPSG:4326 es el formato estándar GPS (Lat/Lon)
gdf_incendios = gpd.GeoDataFrame(df_incendios, geometry=geometria_incendios, crs="EPSG:4326")

# 3. Cruce Espacial (Spatial Join)
print("🧮 Calculando densidad de incendios por manzana...")
# Unimos los puntos de incendios con el polígono de la manzana que los contiene
cruce = gpd.sjoin(gdf_incendios, manzanas, how="inner", predicate="intersects")

# Contamos cuántos incendios hay en cada manzana. 
# Si tu shapefile no tiene CVE_MZA, buscaremos la columna correcta.
# Por lo general, INEGI usa 'CVE_MZA' o 'CVEGEO'
columna_id = 'CVE_MZA' if 'CVE_MZA' in manzanas.columns else manzanas.columns[0]
conteo = cruce.groupby(columna_id).size().reset_index(name='total_incendios')

# 4. Integrar la Variable Objetivo al dataset principal
manzanas = manzanas.merge(conteo, on=columna_id, how='left')
# Las manzanas que no tuvieron incendios tendrán NaN, las rellenamos con 0
manzanas['total_incendios'] = manzanas['total_incendios'].fillna(0)

# 5. Guardar el Dataset Final para la IA
print("💾 Guardando Dataset Final con variables predictoras...")
os.makedirs('data/outputs', exist_ok=True)

# SOLUCIÓN AL ERROR: En lugar de buscar nombres específicos, simplemente 
# eliminamos la columna de geometría que es pesada para el CSV.
df_final = manzanas.drop(columns=['geometry']).copy()

df_final.to_csv("data/outputs/dataset_final.csv", index=False)

print("✅ ¡Proceso completado con éxito!")
print(f"📊 Manzanas procesadas: {len(manzanas)}")
print(f"🔥 Manzanas con al menos 1 incendio registrado: {len(conteo)}")
print(f"📁 Archivo listo para ML: data/outputs/dataset_final.csv")