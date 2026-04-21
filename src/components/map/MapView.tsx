import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function MapView({ onSelect }: any) {
  const [manzanasGeoJSON, setManzanasGeoJSON] = useState<any>(null);
  const [radarActivo, setRadarActivo] = useState(false);

  // 1. CARGA DEL ARCHIVO MAESTRO (Generado por tu Python ETL)
  useEffect(() => {
    fetch('/data/manzanas_datos_produccion.json')
      .then(response => response.json())
      .then(data => setManzanasGeoJSON(data))
      .catch(error => console.error("Error cargando la base espacial:", error));
  }, []);

  // 2. LÓGICA DE ESCANEO (El Filtro Visual)
  const estiloPoligonos = (feature: any) => {
    const hacinamiento = feature.properties.PRO_OCUP_C || 1.0;
    const tipoZona = feature.properties.tipo_zona_calculada || 1;

    if (radarActivo) {
      // MODO RADAR: Solo iluminamos de ROJO las manzanas con Hacinamiento Crítico (> 2.0 personas/cuarto)
      if (hacinamiento > 2.0) {
        return { 
          fillColor: '#ef4444', // Rojo Alerta
          weight: 1.5, 
          opacity: 1, 
          color: '#ef4444', 
          fillOpacity: 0.7 
        };
      }
      // Apagamos el resto de la ciudad para que resalte la alerta
      return { fillColor: '#0a150f', weight: 0.5, opacity: 0.3, color: '#1a3324', fillOpacity: 0.2 };
    }

    // MODO NORMAL: Estética verde táctica de URBIPREX
    return { 
      fillColor: '#10b981', 
      weight: 1, 
      opacity: 0.5, 
      color: '#047857', 
      fillOpacity: 0.1 
    };
  };

  // 3. INTERACTIVIDAD (Clic para enviar datos al Cerebro V4)
  const interactividadManzana = (feature: any, layer: any) => {
    layer.on({
      click: () => {
        onSelect(feature.properties);
      }
    });
  };

  return (
    <div className="relative h-full w-full">
      
      {/* BOTÓN FLOTANTE DEL RADAR TÁCTICO */}
      <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-[1000]">
        <button
          onClick={() => setRadarActivo(!radarActivo)}
          className={`flex items-center gap-2 px-6 py-3 rounded-full font-black text-xs tracking-widest uppercase shadow-2xl transition-all duration-300 border ${
            radarActivo
              ? 'bg-red-600 border-red-400 text-white animate-pulse shadow-[0_0_20px_rgba(220,38,38,0.6)]'
              : 'bg-[#11241a]/90 border-[#1f402d] text-emerald-500 hover:bg-[#1a3324] backdrop-blur-sm'
          }`}
        >
          {radarActivo ? (
            <><span>🚨</span> Radar de Hacinamiento Activado</>
          ) : (
            <><span>📡</span> Activar Radar Táctico (Riesgo Eléctrico)</>
          )}
        </button>
      </div>

      {/* MAPA BASE OSCURO (Estilo Militar/Táctico) */}
      <MapContainer center={[31.690, -106.424]} zoom={12} className="h-full w-full" zoomControl={false}>
        <TileLayer 
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" 
          attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
        />
        
        {/* RENDERIZADO MASIVO DE LA CIUDAD */}
        {manzanasGeoJSON && (
          <GeoJSON 
            data={manzanasGeoJSON} 
            style={estiloPoligonos} 
            onEachFeature={interactividadManzana} 
          />
        )}
      </MapContainer>
    </div>
  );
}