import geopandas as gpd

print("🔍 Leyendo el archivo del INEGI...")
gdf = gpd.read_file("conjunto_de_datos/08m.shp")
print("✅ Columnas exactas que tiene tu archivo:")
print(gdf.columns.tolist())