import geopandas as gpd
import os

# Definimos las carpetas de salida según la arquitectura del proyecto
output_web = "public/data"
output_ml = "data/processed"

# Aseguramos que existan
os.makedirs(output_web, exist_ok=True)
os.makedirs(output_ml, exist_ok=True)

print("🚀 Iniciando procesamiento de datos espaciales (Manzanas y Red Vial)...")

# 1. Leer Red Vial previamente descargada
print("🛣️ Cargando red vial base...")
try:
    # Leemos el archivo que generamos en el script anterior
    edges = gpd.read_file(f"{output_ml}/red_vial_juarez.gpkg", layer='calles')
    print("✅ Red vial cargada exitosamente.")
except Exception as e:
    print("⚠️ No se encontró la red vial. Asegúrate de haber corrido 'generar_base.py' primero.")
    edges = None

# 2. Procesar Manzanas INEGI
print("🏘️ Procesando Manzanas del INEGI...")
ruta_shp = "conjunto_de_datos/08m.shp"

if os.path.exists(ruta_shp):
    # Leemos el shapefile
    manzanas = gpd.read_file(ruta_shp)
    
    # Filtramos por Ciudad Juárez (Clave de Municipio '037' en Chihuahua '08')
    # Y convertimos al sistema de coordenadas global (WGS84)
    juarez_m = manzanas[manzanas['CVE_MUN'] == '037'].to_crs(epsg=4326)
    print(f"✅ Se encontraron {len(juarez_m)} manzanas en Ciudad Juárez.")

    # 3. Guardar GeoPackage Profesional para IA
    print("💾 Guardando Dataset Consolidado para Machine Learning...")
    ruta_gpkg = f"{output_ml}/Dataset_Juarez_URBIPREX.gpkg"
    juarez_m.to_file(ruta_gpkg, layer='manzanas', driver="GPKG")
    
    # Si tenemos las calles, las guardamos en el mismo paquete
    if edges is not None:
        edges.to_file(ruta_gpkg, layer='red_vial', driver="GPKG")

    # 4. Optimizar para Web (React)
    print("🌐 Generando versión ligera de manzanas para el dashboard web...")
    # Simplificamos la geometría (tolerancia de ~10 metros) para que no colapse el navegador
    juarez_m_ligero = juarez_m.copy()
    juarez_m_ligero['geometry'] = juarez_m_ligero['geometry'].simplify(0.0001, preserve_topology=True)

    # Guardamos el GeoJSON ligero en la carpeta pública
    juarez_m_ligero.to_file(f"{output_web}/manzanas.json", driver='GeoJSON')
    
    print("✅ ¡Procesamiento completado con éxito!")
    print(f"📁 Base IA: {ruta_gpkg}")
    print(f"📁 Base Web: {output_web}/manzanas.json")

else:
    print(f"❌ Error: No se encontró el archivo {ruta_shp}. Verifica que la carpeta 'conjunto_de_datos' exista.")