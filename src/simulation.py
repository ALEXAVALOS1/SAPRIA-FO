import math

def get_fire_ellipse(lat, lon, wind_deg, wind_speed_kmh, hours=1):
    """
    Calcula los puntos (lat, lon) de una elipse de propagación de fuego
    basada en la dirección y velocidad del viento.
    
    Modelo simplificado Rothermel (Geométrico):
    - A mayor viento, la elipse es más larga y estrecha.
    - La dirección de la elipse sigue al viento.
    """
    
    # Parámetros de simulación
    # Factor de propagación (ajustable según vegetación, aquí promedio urbano)
    spread_factor = 0.1 
    
    # Longitud del eje mayor (cuánto avanza el fuego)
    # Ejemplo: 20km/h de viento * 1 hora * factor 0.1 = 2km de avance
    major_axis_km = wind_speed_kmh * hours * spread_factor
    minor_axis_km = major_axis_km * 0.4 # El ancho es aprox 40% del largo
    
    center_lat = lat
    center_lon = lon
    
    # Generar puntos del polígono
    points = []
    steps = 36 # Calidad del círculo
    
    # Convertir a radianes la dirección del viento (OpenWeather da grados meteorológicos)
    # Ajuste: 0 grados es Norte. Queremos rotar la elipse.
    rotation_rad = math.radians(wind_deg - 90) 

    for i in range(steps):
        theta = math.radians(i * (360 / steps))
        
        # Ecuación paramétrica de la elipse
        x = (major_axis_km / 2) * math.cos(theta)
        y = (minor_axis_km / 2) * math.sin(theta)
        
        # Desplazar el centro de la elipse para que el fuego empiece en el origen (foco trasero)
        x = x + (major_axis_km / 2)
        
        # Rotar según el viento
        x_rot = x * math.cos(rotation_rad) - y * math.sin(rotation_rad)
        y_rot = x * math.sin(rotation_rad) + y * math.cos(rotation_rad)
        
        # Convertir km a grados de lat/lon (Aprox para distancias cortas)
        # 1 grado lat ~= 111km
        delta_lat = y_rot / 111.0
        # 1 grado lon ~= 111km * cos(lat)
        delta_lon = x_rot / (111.0 * math.cos(math.radians(center_lat)))
        
        points.append([center_lat + delta_lat, center_lon + delta_lon])
        
    return points