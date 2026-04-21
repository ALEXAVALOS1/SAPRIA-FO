import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap, Marker, Popup, Polyline, CircleMarker, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// LA RUTA CORREGIDA: Apunta a tu carpeta "map"
import ManzanasLayer from './map/ManzanasLayer';

function FlyToLocation({ pos }: { pos: [number, number] | null }) {
  const map = useMap();
  useEffect(() => { if (pos) map.flyTo(pos, 15, { duration: 1.5 }); }, [pos, map]);
  return null;
}

const fireStationIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #2563eb; border: 2px solid white; border-radius: 8px; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.5);"><svg style="width:16px;height:16px;color:white;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg></div>`,
  iconSize: [26, 26], iconAnchor: [13, 13], popupAnchor: [0, -15],
});

const estacionesBomberos = [
  { id: 1, nombre: "Estación 1 (Central)", lat: 31.7494, lon: -106.4724, desc: "Heroico Colegio Militar" },
  { id: 2, nombre: "Estación 2", lat: 31.7374, lon: -106.4595, desc: "Ignacio Ramírez" },
  { id: 3, nombre: "Estación 3", lat: 31.7174, lon: -106.4728, desc: "Sanders y Sevilla" },
  { id: 4, nombre: "Estación 4", lat: 31.6568, lon: -106.3662, desc: "Gómez Morín (Zaragoza)" },
  { id: 5, nombre: "Estación 5", lat: 31.6661, lon: -106.4355, desc: "Carlos Amaya" },
  { id: 6, nombre: "Estación 6", lat: 31.6253, lon: -106.3980, desc: "Eco 2000" },
  { id: 7, nombre: "Estación 7", lat: 31.6429, lon: -106.3768, desc: "Salvárcar" },
  { id: 8, nombre: "Estación 8", lat: 31.6420, lon: -106.4526, desc: "Barranco Azul" },
  { id: 9, nombre: "Estación 9", lat: 31.7735, lon: -106.5613, desc: "Anapra" }
];

interface MapProps {
  searchPos: [number, number] | null; layers: any; filtroRiesgo: string;
  simulador: { activo: boolean, temp: number, viento: number, humedad: number, trafico: number };
  setSelectedManzana: (manzana: any) => void; selectedManzana: any; mapStyle: string;
}

export default function MapSection({ searchPos, layers, filtroRiesgo, simulador, setSelectedManzana, selectedManzana, mapStyle }: MapProps) {
  const juarezCenter: [number, number] = [31.7333, -106.4833];
  const [incidentes, setIncidentes] = useState<any[]>([]);

  useEffect(() => {
    fetch('/data/incendios_reales.json')
      .then(res => res.json())
      .then(data => {
        let parsed = [];
        
        // DECODIFICADOR 1: Si es formato GeoJSON
        if (data.type === "FeatureCollection" && data.features) {
          parsed = data.features.map((f: any, i: number) => {
            const coords = f.geometry?.coordinates;
            return {
              id: i,
              lat: coords ? coords[1] : null,
              lon: coords ? coords[0] : null,
              fecha: f.properties?.fecha || f.properties?.FECHA || 'S/F',
              tipo: f.properties?.tipo || f.properties?.TIPO || 'Incidente Reportado'
            };
          });
        } 
        // DECODIFICADOR 2: Si es un JSON normal
        else {
          const rawList = data.features ? data.features : data;
          parsed = rawList.map((item: any, index: number) => {
            const target = item.properties || item;
            const keys = Object.keys(target);
            const latKey = keys.find(k => k.toLowerCase().includes('lat') || k.toLowerCase() === 'y');
            const lonKey = keys.find(k => k.toLowerCase().includes('lon') || k.toLowerCase().includes('lng') || k.toLowerCase() === 'x');
            const fechaKey = keys.find(k => k.toLowerCase().includes('fecha') || k.toLowerCase().includes('date'));
            const tipoKey = keys.find(k => k.toLowerCase().includes('tipo') || k.toLowerCase().includes('incidente') || k.toLowerCase().includes('causa'));

            return {
              id: index,
              lat: latKey ? parseFloat(target[latKey]) : null,
              lon: lonKey ? parseFloat(target[lonKey]) : null,
              fecha: fechaKey ? target[fechaKey] : 'S/F',
              tipo: tipoKey ? target[tipoKey] : 'Incidente'
            };
          });
        }
        
        const validos = parsed.filter((i: any) => i.lat !== null && i.lon !== null && !isNaN(i.lat) && !isNaN(i.lon));
        setIncidentes(validos);
      })
      .catch(err => console.error("Error leyendo incendios_reales.json:", err));
  }, []);

  let tileUrl = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"; 
  if (mapStyle === 'satellite') tileUrl = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
  else if (mapStyle === 'light' || (mapStyle === 'auto' && !layers.manzanas)) tileUrl = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
  else if (mapStyle === 'dark' || (mapStyle === 'auto' && layers.manzanas)) tileUrl = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

  let rutaPosiciones: [number, number][] = [];
  if (selectedManzana && selectedManzana.lat && selectedManzana.lon) {
    let estCercana = estacionesBomberos.reduce((prev, curr) => {
      const dPrev = Math.pow(prev.lat - selectedManzana.lat, 2) + Math.pow(prev.lon - selectedManzana.lon, 2);
      const dCurr = Math.pow(curr.lat - selectedManzana.lat, 2) + Math.pow(curr.lon - selectedManzana.lon, 2);
      return dCurr < dPrev ? curr : prev;
    });
    rutaPosiciones = [[estCercana.lat, estCercana.lon], [selectedManzana.lat, selectedManzana.lon]];
  }

  return (
    <MapContainer center={juarezCenter} zoom={12} zoomControl={false} className="w-full h-full relative z-0">
      <TileLayer key={tileUrl} url={tileUrl} attribution='&copy; OpenStreetMap' />
      {mapStyle === 'satellite' && <TileLayer url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png" zIndex={10} />}
      <FlyToLocation pos={searchPos} />

      {layers.mapas_calor && incidentes.map((inc) => (
        <Circle key={`heat-${inc.id}`} center={[inc.lat, inc.lon]} pathOptions={{ fillColor: '#ef4444', color: 'transparent', fillOpacity: 0.05 }} radius={600} interactive={false} />
      ))}

      {layers.manzanas && <ManzanasLayer filtroRiesgo={filtroRiesgo} simulador={simulador} setSelectedManzana={setSelectedManzana} mapStyle={mapStyle} />}

      {layers.historial && incidentes.map(inc => (
        <CircleMarker key={`hist-${inc.id}`} center={[inc.lat, inc.lon]} radius={5} pathOptions={{ color: '#ffffff', fillColor: '#ef4444', fillOpacity: 0.9, weight: 1.5 }}>
          <Popup className="custom-popup">
            <div className="text-left font-sans p-1">
              <strong className="text-red-500 text-xs block mb-1">🔥 {inc.tipo}</strong>
              <span className="text-gray-600 text-[10px] block font-bold">Fecha: {inc.fecha}</span>
            </div>
          </Popup>
        </CircleMarker>
      ))}

      {layers.unidades && estacionesBomberos.map(est => (
        <Marker key={est.id} position={[est.lat, est.lon]} icon={fireStationIcon}>
          <Popup className="custom-popup"><div className="text-center"><strong className="text-blue-600 text-xs block">{est.nombre}</strong></div></Popup>
        </Marker>
      ))}

      {rutaPosiciones.length > 0 && layers.unidades && <Polyline positions={rutaPosiciones} pathOptions={{ color: '#3b82f6', weight: 3, dashArray: '8, 12' }} />}
    </MapContainer>
  );
}