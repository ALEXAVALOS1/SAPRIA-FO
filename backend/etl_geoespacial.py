import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
import os

# --- 0. CONFIGURACIÓN DE RUTAS ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_manzanas = os.path.join(base_dir, "public", "data", "manzanas_datos.json")
ruta_denue = os.path.join(base_dir, "conjunto_de_datos", "denue_inegi_08_.csv")
ruta_iter = os.path.join(base_dir, "conjunto_de_datos", "RESAGEBURB_08CSV20.csv") 
ruta_salida = os.path.join(base_dir, "public", "data", "manzanas_datos_produccion.json")

def ejecutar_etl_completo():
    print("="*50)
    print("INICIANDO PIPELINE ETL GEOESPACIAL V2 (URBIPREX)")
    print("="*50)
    
    # --- 1. EXTRACT (Extracción de Datos) ---
    print("\n[1/3] EXTRAYENDO DATOS OFICIALES (MAPA, DENUE Y CENSO)...")
    gdf_manzanas = gpd.read_file(ruta_manzanas)
    print(f" -> Mapa base cargado: {len(gdf_manzanas)} manzanas.")

    df_denue = pd.read_csv(ruta_denue, encoding='latin1', low_memory=False)
    # Blindaje DENUE: Forzamos minúsculas para evitar errores buscando 'municipio' o 'latitud'
    df_denue.columns = df_denue.columns.str.strip().str.lower()
    print(f" -> DENUE cargado: {len(df_denue)} registros comerciales.")

    # SOLUCIÓN QUIRÚRGICA: utf-8-sig destruye el caracter fantasma (BOM) del INEGI
    # Al cargar el ITER, el INEGI usa asteriscos '*' para ocultar datos. Los convertimos a nulos (NaN).
    df_iter = pd.read_csv(ruta_iter, encoding='utf-8-sig', low_memory=False, na_values=['*'])
    
    # BLINDAJE ITER: Forzamos a que todos los títulos sean mayúsculas y sin espacios invisibles
    df_iter.columns = df_iter.columns.str.strip().str.upper()
    print(f" -> Censo ITER cargado: {len(df_iter)} registros demográficos.")

    # --- 2. TRANSFORM (Transformación, Cruce y Feature Engineering) ---
    print("\n[2/3] INICIANDO PROCESAMIENTO ESPACIAL Y DEMOGRÁFICO...")

    # A) Procesar el Censo (ITER) para crear el CVEGEO y cruzarlo con el mapa
    print(" -> Construyendo claves geográficas del Censo y extrayendo Nutriente 3 (Hacinamiento)...")
    
    # Filtramos solo las filas que son manzanas reales 
    df_iter = df_iter[df_iter['MZA'] != 0].copy()
    
    # Construimos el CVEGEO de 16 dígitos uniendo Entidad(2) + Municipio(3) + Localidad(4) + AGEB(4) + Manzana(3)
    # Nota de blindaje: Reemplazamos '.0' en caso de que Pandas haya leído los IDs como flotantes (ej. 8.0 -> 8)
    df_iter['ENTIDAD'] = df_iter['ENTIDAD'].astype(str).str.replace('.0', '', regex=False).str.zfill(2)
    df_iter['MUN'] = df_iter['MUN'].astype(str).str.replace('.0', '', regex=False).str.zfill(3)
    df_iter['LOC'] = df_iter['LOC'].astype(str).str.replace('.0', '', regex=False).str.zfill(4)
    df_iter['AGEB'] = df_iter['AGEB'].astype(str).str.replace('.0', '', regex=False).str.zfill(4)
    df_iter['MZA'] = df_iter['MZA'].astype(str).str.replace('.0', '', regex=False).str.zfill(3)
    
    df_iter['CVEGEO'] = df_iter['ENTIDAD'] + df_iter['MUN'] + df_iter['LOC'] + df_iter['AGEB'] + df_iter['MZA']

    # Extraemos el indicador de riesgo eléctrico: Promedio de ocupantes por cuarto (PRO_OCUP_C)
    df_iter_limpio = df_iter[['CVEGEO', 'PRO_OCUP_C']].copy()
    df_iter_limpio['PRO_OCUP_C'] = pd.to_numeric(df_iter_limpio['PRO_OCUP_C'], errors='coerce').fillna(1.0)

    # B) Procesar DENUE (Uso de Suelo)
    if 'municipio' in df_denue.columns:
        df_denue = df_denue[df_denue['municipio'].str.contains('juárez', case=False, na=False)]
    
    geometria_denue = [Point(xy) for xy in zip(df_denue.longitud, df_denue.latitud)]
    gdf_denue = gpd.GeoDataFrame(df_denue, geometry=geometria_denue, crs="EPSG:4326")
    
    gdf_manzanas = gdf_manzanas.to_crs("EPSG:4326")
    print(" -> Realizando intersección espacial con DENUE (calculando uso de suelo)...")
    join_espacial = gpd.sjoin(gdf_denue, gdf_manzanas, how="inner", predicate="within")
    conteo_negocios = join_espacial.groupby('CVEGEO').size().reset_index(name='total_negocios')
    
    # C) FUSIÓN MAESTRA (Unimos Mapa + Negocios + Censo)
    gdf_manzanas = gdf_manzanas.merge(conteo_negocios, on='CVEGEO', how='left')
    gdf_manzanas['total_negocios'] = gdf_manzanas['total_negocios'].fillna(0)
    
    # Unimos el Nutriente 3 (ITER)
    gdf_manzanas = gdf_manzanas.merge(df_iter_limpio, on='CVEGEO', how='left')
    gdf_manzanas['PRO_OCUP_C'] = gdf_manzanas['PRO_OCUP_C'].fillna(1.0) # 1 persona/cuarto por defecto si no hay dato

    def determinar_uso(row):
        if row['total_negocios'] >= 3:
            return 3 # Comercial / Industrial
        elif row.get('poblacion_total', 0) > 10:
            return 2 # Residencial
        else:
            return 1 # Baldío / Parque / Lote
    gdf_manzanas['tipo_zona_calculada'] = gdf_manzanas.apply(determinar_uso, axis=1)
    
    # D) Distancia a Bomberos (Metraje exacto)
    print(" -> Calculando distancias geodésicas a estaciones de bomberos...")
    estaciones = [
        Point(-106.4724, 31.7494), Point(-106.4595, 31.7374), Point(-106.4728, 31.7174),
        Point(-106.3662, 31.6568), Point(-106.4355, 31.6661), Point(-106.3980, 31.6253),
        Point(-106.3768, 31.6429), Point(-106.4526, 31.6420), Point(-106.5613, 31.7735)
    ]
    gdf_estaciones = gpd.GeoDataFrame(geometry=estaciones, crs="EPSG:4326")
    gdf_manzanas_utm = gdf_manzanas.to_crs("EPSG:32613")
    gdf_estaciones_utm = gdf_estaciones.to_crs("EPSG:32613")
    
    def min_distancia(geom):
        return gdf_estaciones_utm.distance(geom).min()
    gdf_manzanas['distancia_bomberos_m'] = gdf_manzanas_utm.geometry.apply(min_distancia)

    # --- 3. LOAD (Exportar) ---
    print("\n[3/3] EXPORTANDO ARCHIVO MAESTRO...")
    columnas_mantener = [
        'CVEGEO', 'poblacion_total', 'densidad_vial', 'total_negocios', 
        'tipo_zona_calculada', 'distancia_bomberos_m', 'PRO_OCUP_C', 'geometry'
    ]
    columnas_reales = [c for c in columnas_mantener if c in gdf_manzanas.columns]
    gdf_manzanas_limpio = gdf_manzanas[columnas_reales]

    gdf_manzanas_limpio.to_file(ruta_salida, driver="GeoJSON")
    
    print("="*50)
    print(f"✅ ¡ETL FINALIZADO CON ÉXITO! Archivo de producción generado.")
    print("Todas las variables estructurales, demográficas y espaciales han sido fusionadas.")
    print("="*50)

if __name__ == "__main__":
    ejecutar_etl_completo()