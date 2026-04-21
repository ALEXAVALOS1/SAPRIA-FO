import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json
import os

print("🔥 INICIANDO INYECCIÓN DE INCENDIOS REALES A LAS MANZANAS...")

ruta_dataset = "data/outputs/dataset_final.csv"
ruta_shp = "conjunto_de_datos/08m.shp"
ruta_incendios = "public/data/incendios_reales.json"

if not os.path.exists(ruta_incendios) or not os.path.exists(ruta_shp):
    print("❌ Error: Faltan archivos base.")
    exit()

try:
    print("1️⃣ Cargando el Dataset actual (para borrar los incendios falsos)...")
    df_actual = pd.read_csv(ruta_dataset)
    
    print("2️⃣ Leyendo el archivo de coordenadas de incendios reales...")
    with open(ruta_incendios, 'r', encoding='utf-8') as f:
        datos_fuego = json.load(f)
        
    # ⚠️ CORRECCIÓN: Revisamos si es un diccionario (GeoJSON) o una lista plana (JSON normal)
    if isinstance(datos_fuego, dict):
        lista_puntos = datos_fuego.get('features', [datos_fuego])
    else:
        lista_puntos = datos_fuego
        
    coordenadas_validas = []
    
    # Extraemos lat/lon
    for item in lista_puntos:
        if not isinstance(item, dict):
            continue
            
        target = item.get('properties', item)
        keys = target.keys()
        
        lat_key = next((k for k in keys if 'lat' in k.lower() or k.lower() == 'y'), None)
        lon_key = next((k for k in keys if 'lon' in k.lower() or 'lng' in k.lower() or k.lower() == 'x'), None)
        
        if lat_key and lon_key:
            try:
                lat = float(target[lat_key])
                lon = float(target[lon_key])
                if not pd.isna(lat) and not pd.isna(lon):
                    coordenadas_validas.append(Point(lon, lat)) # Point toma (X, Y) -> (Lon, Lat)
            except:
                pass

    print(f"✅ Se extrajeron {len(coordenadas_validas)} puntos de incendio reales.")
    
    if len(coordenadas_validas) == 0:
        print("❌ Error: No se encontraron coordenadas válidas en el archivo JSON.")
        exit()
        
    # Creamos un mapa de puntos con Geopandas
    gdf_puntos = gpd.GeoDataFrame(geometry=coordenadas_validas, crs="EPSG:4326")
    
    print("3️⃣ Cargando la cartografía de manzanas (08m.shp)...")
    gdf_manzanas = gpd.read_file(ruta_shp)
    
    # Asegurarnos de que ambos mapas hablen el mismo idioma espacial (Coordenadas GPS estándar)
    gdf_manzanas = gdf_manzanas.to_crs("EPSG:4326")
    
    print("4️⃣ CRUZANDO MAPAS: Contando qué incendios caen dentro de qué manzana...")
    # SJOIN: Spatial Join (Intersección Espacial)
    interseccion = gpd.sjoin(gdf_puntos, gdf_manzanas, how="inner", predicate="intersects")
    
    # Agrupamos por la clave de la manzana para saber el total real
    col_cvegeo = [c for c in interseccion.columns if 'CVEGEO' in c.upper()][0]
    conteo_real = interseccion.groupby(col_cvegeo).size().reset_index(name='incendios_reales')
    conteo_real.rename(columns={col_cvegeo: 'CVEGEO'}, inplace=True)
    
    print("5️⃣ Inyectando la verdad al Dataset maestro...")
    # Al hacer merge, las manzanas que no tuvieron incendios tendrán NaN (vacío)
    df_final = pd.merge(df_actual, conteo_real, on='CVEGEO', how='left')
    
    # Sobrescribimos la columna 'total_incendios' (borrando los falsos) por los reales (o 0)
    if 'total_incendios' in df_final.columns:
        df_final.drop(columns=['total_incendios'], inplace=True)
        
    df_final['total_incendios'] = df_final['incendios_reales'].fillna(0).astype(int)
    df_final.drop(columns=['incendios_reales'], inplace=True)
    
    df_final.to_csv(ruta_dataset, index=False)
    
    total_fuego_mapeado = df_final['total_incendios'].sum()
    manzanas_afectadas = (df_final['total_incendios'] > 0).sum()
    
    print("-" * 50)
    print("✅ ¡BASE DE DATOS 100% REAL COMPLETADA!")
    print(f"🔥 Total de incendios asignados a manzanas: {total_fuego_mapeado}")
    print(f"🏘️ Manzanas que realmente han tenido incendios: {manzanas_afectadas}")
    print("-" * 50)
    print("🚀 AHORA SÍ. VE A CORRER EL ENTRENAMIENTO DE LA IA OTRA VEZ.")

except Exception as e:
    print(f"❌ Error fatal: {e}")