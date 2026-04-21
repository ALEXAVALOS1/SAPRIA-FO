import pandas as pd
import numpy as np
import os
import json

print("📊 INICIANDO INYECCIÓN DE DATOS DEMOGRÁFICOS REALES (CENSO INEGI)...")

ruta_dataset_actual = "data/outputs/dataset_final.csv"
ruta_censo = "data/censo_chihuahua.csv"
ruta_json_frontend = "public/data/manzanas_datos.json"

if not os.path.exists(ruta_censo):
    print(f"❌ Error: No se encuentra {ruta_censo}. Descárgalo del INEGI y ponlo en la carpeta 'data'.")
    exit()

try:
    print("1️⃣ Cargando el Dataset actual de tu proyecto...")
    df_actual = pd.read_csv(ruta_dataset_actual)
    
    print("2️⃣ Cargando la base de datos del Censo 2020...")
    # El INEGI a veces usa diferentes codificaciones, intentamos UTF-8 y si no, latin1
    try:
        df_censo = pd.read_csv(ruta_censo, dtype=str)
    except UnicodeDecodeError:
        df_censo = pd.read_csv(ruta_censo, dtype=str, encoding='latin1')
        
    print("3️⃣ Filtrando solo Ciudad Juárez y construyendo el CVEGEO...")
    # Filtramos el municipio 037 (Juárez)
    df_juarez = df_censo[df_censo['MUN'] == '037'].copy()
    
    # El INEGI separa la clave, la volvemos a unir como bloque de Lego
    df_juarez['ENTIDAD'] = df_juarez['ENTIDAD'].astype(str).str.zfill(2)
    df_juarez['MUN'] = df_juarez['MUN'].astype(str).str.zfill(3)
    df_juarez['LOC'] = df_juarez['LOC'].astype(str).str.zfill(4)
    df_juarez['AGEB'] = df_juarez['AGEB'].astype(str).str.zfill(4)
    df_juarez['MZA'] = df_juarez['MZA'].astype(str).str.zfill(3)
    
    # Creamos el CVEGEO maestro (16 dígitos)
    df_juarez['CVEGEO'] = df_juarez['ENTIDAD'] + df_juarez['MUN'] + df_juarez['LOC'] + df_juarez['AGEB'] + df_juarez['MZA']
    
    # Extraemos solo las columnas vitales: Clave y Población Total (POBTOT)
    # Limpiamos los asteriscos '*' que el INEGI pone en manzanas sin casas
    df_juarez['POBTOT'] = pd.to_numeric(df_juarez['POBTOT'].replace('*', '0').replace('N/D', '0'), errors='coerce').fillna(0)
    
    df_demografia = df_juarez[['CVEGEO', 'POBTOT']].copy()
    df_demografia.rename(columns={'POBTOT': 'poblacion_real'}, inplace=True)
    
    print("4️⃣ Cruzando los datos reales con tu Dataset espacial...")
    df_final = pd.merge(df_actual, df_demografia, on='CVEGEO', how='left')
    
    # Sustituir la población aleatoria por la real
    df_final['poblacion_total'] = df_final['poblacion_real'].fillna(0)
    
    # Recalcular la Densidad Poblacional
    df_final['densidad_pob'] = df_final['poblacion_total'] / 1.0 
    
    df_final.drop(columns=['poblacion_real'], inplace=True)
    
    print("5️⃣ Guardando el nuevo Dataset Saneado y 100% Real para la IA...")
    df_final.to_csv(ruta_dataset_actual, index=False)

    # 6. Actualizar el Frontend directamente
    if os.path.exists(ruta_json_frontend):
        print("6️⃣ Inyectando población real directamente en el Mapa de React...")
        with open(ruta_json_frontend, 'r', encoding='utf-8') as f:
            geo_data = json.load(f)
            
        pop_dict = df_final.set_index('CVEGEO')['poblacion_total'].to_dict()
        
        for feature in geo_data['features']:
            cve = feature['properties'].get('CVEGEO')
            if cve in pop_dict:
                feature['properties']['poblacion_total'] = int(pop_dict[cve])
                
        with open(ruta_json_frontend, 'w', encoding='utf-8') as f:
            json.dump(geo_data, f)
    
    print("-" * 50)
    print("✅ ¡ÉXITO ROTUNDO! DATOS DEL INEGI INTEGRADOS.")
    print(f"Habitantes Contabilizados en Juárez: {df_final['poblacion_total'].sum():,.0f}")
    print(f"Manzana más poblada: {df_final['poblacion_total'].max():,.0f} habitantes.")
    print("-" * 50)

except Exception as e:
    print(f"❌ Error fatal: {e}")