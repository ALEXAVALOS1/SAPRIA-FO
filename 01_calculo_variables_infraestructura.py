import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import json
import os

print("🚀 Iniciando Cálculo COMPLETO de Variables de Infraestructura (Semana 6)...")

# 1. Cargar el dataset final y las geometrías de las manzanas
print("📊 Cargando dataset_final.csv y geometrías...")
ruta_csv = "data/outputs/dataset_final.csv"
df_final = pd.read_csv(ruta_csv)

manzanas = gpd.read_file("data/processed/Dataset_Juarez_URBIPREX.gpkg", layer='manzanas')
manzanas_metric = manzanas.to_crs(epsg=32613)

# Calculamos el área de cada manzana en kilómetros cuadrados (km²)
manzanas_metric['area_km2'] = manzanas_metric.geometry.area / 1_000_000

# -------------------------------------------------------------------
# PASO A: DISTANCIA A ESTACIONES DE BOMBEROS (Mantenemos lo que ya funcionaba)
# -------------------------------------------------------------------
print("🚒 Verificando distancia a estaciones de bomberos...")
if 'acceso_bomberos_km' not in df_final.columns:
    centroides = manzanas_metric.geometry.centroid
    with open("public/data/bomberos.json", 'r', encoding='utf-8') as f:
        bomberos_data = json.load(f)
    df_bomberos = pd.DataFrame(bomberos_data)
    gdf_bomberos = gpd.GeoDataFrame(df_bomberos, geometry=[Point(xy) for xy in zip(df_bomberos['lon'], df_bomberos['lat'])], crs="EPSG:4326")
    distancias_metros = centroides.apply(lambda x: gdf_bomberos.to_crs(epsg=32613).distance(x).min())
    df_final['acceso_bomberos_km'] = round(distancias_metros / 1000, 2)

# -------------------------------------------------------------------
# PASO B: INTERSECCIONES POR KM² (Nuevas Variables)
# -------------------------------------------------------------------
print("🚦 Calculando densidad de intersecciones (cruces de calles)...")
# Cargamos los nodos (intersecciones) de la red vial
nodos = gpd.read_file("data/processed/red_vial_juarez.gpkg", layer='nodos')
nodos_metric = nodos.to_crs(epsg=32613)

# Cruzamos los puntos de intersección con los polígonos de las manzanas
cruce_nodos = gpd.sjoin(nodos_metric, manzanas_metric, how='inner', predicate='intersects')
conteo_nodos = cruce_nodos.groupby('CVEGEO').size().reset_index(name='total_intersecciones')

# -------------------------------------------------------------------
# PASO C: DENSIDAD VIAL Y TIPO VIAL (Nuevas Variables)
# -------------------------------------------------------------------
print("🛣️ Calculando densidad y tipos de vialidades...")
# Cargamos las calles
calles = gpd.read_file("data/processed/red_vial_juarez.gpkg", layer='calles')
calles_metric = calles.to_crs(epsg=32613)

# Calculamos la longitud de cada calle en kilómetros
calles_metric['longitud_km'] = calles_metric.geometry.length / 1000

# Clasificamos las calles en "Principal" (1) o "Secundaria/Otra" (0)
vias_principales = ['primary', 'secondary', 'trunk', 'motorway']
# Ojo: OSMnx a veces guarda las clasificaciones en listas si la calle tiene varios tipos
calles_metric['es_principal'] = calles_metric['highway'].apply(
    lambda x: 1 if isinstance(x, str) and x in vias_principales else (1 if isinstance(x, list) and any(i in vias_principales for i in x) else 0)
)

# Para un cruce rápido sin cortar geometrías pesadas, usamos el centroide de cada calle
calles_puntos = calles_metric.copy()
calles_puntos['geometry'] = calles_metric.geometry.centroid

cruce_calles = gpd.sjoin(calles_puntos, manzanas_metric, how='inner', predicate='intersects')

# Agrupamos por manzana para sumar los kilómetros de calles y calcular el porcentaje de principales
agrupado_calles = cruce_calles.groupby('CVEGEO').agg(
    km_totales=('longitud_km', 'sum'),
    km_principales=('es_principal', lambda x: (x * cruce_calles.loc[x.index, 'longitud_km']).sum())
).reset_index()

# -------------------------------------------------------------------
# PASO D: CONSOLIDAR TODO EN EL DATASET FINAL
# -------------------------------------------------------------------
print("🧮 Consolidando cálculos finales...")

# Preparamos un DataFrame temporal con el Área para hacer los cálculos
df_calc = manzanas_metric[['CVEGEO', 'area_km2']].copy()

# Unimos los conteos
df_calc = df_calc.merge(conteo_nodos, on='CVEGEO', how='left').fillna(0)
df_calc = df_calc.merge(agrupado_calles, on='CVEGEO', how='left').fillna(0)

# Calculamos las fórmulas exigidas por tu documento:
# 1. Intersecciones: Número de cruces / Área en km²
df_calc['intersecciones_km2'] = round(df_calc['total_intersecciones'] / df_calc['area_km2'].replace(0, 0.0001), 2)

# 2. Densidad Vial: Km de calles / Área en km²
df_calc['densidad_vial'] = round(df_calc['km_totales'] / df_calc['area_km2'].replace(0, 0.0001), 2)

# 3. Tipo Vial: % de vías principales (0 a 100)
df_calc['tipo_vial_pct'] = round((df_calc['km_principales'] / df_calc['km_totales'].replace(0, 0.0001)) * 100, 1)

# Pasamos las nuevas variables al dataset final (cuidando de no duplicar si ya existían)
columnas_nuevas = ['intersecciones_km2', 'densidad_vial', 'tipo_vial_pct']
for col in columnas_nuevas:
    if col in df_final.columns:
        df_final.drop(columns=[col], inplace=True)

df_final = df_final.merge(df_calc[['CVEGEO'] + columnas_nuevas], on='CVEGEO', how='left')

# Rellenamos los vacíos (manzanas sin calles adentro) con ceros
df_final[columnas_nuevas] = df_final[columnas_nuevas].fillna(0)

# Guardamos
df_final.to_csv(ruta_csv, index=False)

print("✅ ¡SEMANA 6 COMPLETADA AL 100%!")
print("Nuevas variables agregadas al dataset:")
print(f" - densidad_vial (Promedio: {df_final['densidad_vial'].mean():.2f} km/km²)")
print(f" - intersecciones_km2 (Promedio: {df_final['intersecciones_km2'].mean():.2f} cruces/km²)")
print(f" - tipo_vial_pct (Promedio: {df_final['tipo_vial_pct'].mean():.2f}% vías principales)")