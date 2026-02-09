def calculate_fwi(temp, humidity, wind_kph):
    """
    Calcula el Índice Meteorológico de Incendios (FWI) aproximado.
    Basado en el sistema canadiense estándar.
    Retorna: (Valor Numérico, Categoría, Color)
    """
    # Factor de Humedad (FFMC simplificado)
    # A menor humedad, mayor combustibilidad del suelo
    if humidity < 10: hum_factor = 10
    elif humidity < 30: hum_factor = 6
    elif humidity < 50: hum_factor = 3
    else: hum_factor = 1
    
    # Factor de Viento (ISI simplificado)
    # El viento duplica la tasa de propagación exponencialmente
    wind_factor = 1 + (wind_kph / 10)
    
    # Factor Temperatura
    temp_factor = 1
    if temp > 30: temp_factor = 2
    
    # Cálculo del índice FWI
    fwi_score = (hum_factor * wind_factor * temp_factor)
    
    # Categorización Estándar
    if fwi_score < 5:
        return fwi_score, "BAJO", "#10B981" # Verde
    elif fwi_score < 15:
        return fwi_score, "MODERADO", "#3B82F6" # Azul
    elif fwi_score < 30:
        return fwi_score, "ALTO", "#F59E0B" # Amarillo
    elif fwi_score < 60:
        return fwi_score, "MUY ALTO", "#F97316" # Naranja
    else:
        return fwi_score, "EXTREMO", "#EF4444" # Rojo