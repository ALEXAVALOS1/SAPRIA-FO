def is_point_in_polygon(lat, lon, polygon_points):
    """
    Algoritmo 'Ray Casting' para determinar si una coordenada (lat, lon)
    está dentro de un polígono (lista de [lat, lon]).
    Retorna True si está dentro, False si no.
    """
    x, y = lat, lon
    n = len(polygon_points)
    inside = False
    
    p1x, p1y = polygon_points[0]
    for i in range(n + 1):
        p2x, p2y = polygon_points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
        
    return inside

def analyze_impact(fire_polygon, df_infra):
    """
    Analiza qué infraestructuras caen dentro de la zona de fuego.
    Retorna un DataFrame con los edificios afectados.
    """
    if df_infra.empty or not fire_polygon:
        return []
    
    afectados = []
    
    for _, row in df_infra.iterrows():
        # Verificar si la coordenada del edificio está en el polígono
        if is_point_in_polygon(row['lat'], row['lon'], fire_polygon):
            afectados.append({
                "nombre": row['nombre'],
                "tipo": row['tipo'],
                "lat": row['lat'],
                "lon": row['lon'],
                "color": row['color'],
                "icon": row['icon']
            })
            
    return afectados