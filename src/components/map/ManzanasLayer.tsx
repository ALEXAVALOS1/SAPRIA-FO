import React, { useEffect, useState } from 'react';
import { GeoJSON } from 'react-leaflet';
import L from 'leaflet';

interface ManzanasLayerProps {
  filtroRiesgo: string;
  simulador: { activo: boolean, temp: number, viento: number, humedad: number, trafico: number };
  setSelectedManzana: (manzana: any) => void;
  mapStyle?: string;
}

export default function ManzanasLayer({ filtroRiesgo, simulador, setSelectedManzana, mapStyle }: ManzanasLayerProps) {
  const [geoData, setGeoData] = useState<any>(null);

  useEffect(() => {
    fetch('/data/manzanas_datos_produccion.json')
      .then((res) => res.json())
      .then((data) => setGeoData(data))
      .catch((err) => console.error("Error cargando capa:", err));
  }, []);

  const calcularRiesgo = (feature: any) => {
    let riesgoActual = feature.properties.riesgo_base || 'BAJO';
    let nivelBase = riesgoActual === 'ALTO' ? 3 : riesgoActual === 'MEDIO' ? 2 : 1; 

    if (simulador.activo) {
      if (simulador.temp >= 40) nivelBase += 1; 
      if (simulador.viento >= 45) nivelBase += 1; 
      if (simulador.humedad <= 20) nivelBase += 1; 
    }

    const nivelFinal = Math.min(Math.max(nivelBase, 1), 3);

    if (nivelFinal === 3) return { texto: 'ALTO', color: '#ef4444', textClass: 'text-red-500' };
    if (nivelFinal === 2) return { texto: 'MEDIO', color: '#facc15', textClass: 'text-yellow-500' };
    return { texto: 'BAJO', color: '#10b981', textClass: 'text-emerald-500' };
  };

  const estiloManzana = (feature: any) => {
    const riesgo = calcularRiesgo(feature);
    
    // 🚨 CALIBRACIÓN QUIRÚRGICA DEL RADAR
    const hacinamiento = Number(feature.properties.PRO_OCUP_C) || 1.0;
    
    // Nivel 1.5 es el umbral real de peligro eléctrico/estructural
    const esRiesgoEstructural = hacinamiento >= 1.5; 

    // 📡 LÓGICA DEL RADAR TÁCTICO
    if (filtroRiesgo === 'CRITICOS') {
      if (esRiesgoEstructural || riesgo.texto === 'ALTO') {
        // Alerta Máxima: Rojo Brillante
        return {
          fillColor: '#ef4444', 
          weight: 1.5,
          opacity: 1,
          color: '#ef4444',
          fillOpacity: 0.8,
          interactive: true
        };
      } else {
        // Zona Segura: Casi invisible para que resalte el rojo
        return {
          fillColor: '#0a150f',
          weight: 0.5,
          opacity: 0.1,
          color: '#1a3324',
          fillOpacity: 0.05,
          interactive: true
        };
      }
    }

    // 🟢 MODO NORMAL (TODOS)
    const baseOpacity = mapStyle === 'satellite' ? 0.3 : 0.4;
    const activeOpacity = simulador.activo ? 0.6 : baseOpacity;

    return {
      fillColor: riesgo.color,
      weight: 1,
      opacity: 0.8,
      color: mapStyle === 'satellite' ? '#ffffff' : '#112a1c',
      fillOpacity: activeOpacity,
      interactive: true 
    };
  };

  const onEachManzana = (feature: any, layer: L.Layer) => {
    const riesgo = calcularRiesgo(feature);
    const props = feature.properties;

    const tooltipContent = `
      <div style="background-color: #0b1c14; border: 1px solid #1f402d; padding: 12px; border-radius: 8px; color: white; min-width: 200px;">
        <h4 style="font-size: 13px; font-weight: bold; margin: 0 0 4px 0;">📊 Analítica de Cuadrante</h4>
        <div style="width: 100%; height: 1px; background-color: #1f402d; margin-bottom: 8px;"></div>
        <p style="margin: 0; font-size: 12px; color: #9ca3af;">Población: <span style="color: white; font-weight: bold;">${props.poblacion_total || props.POBTOT || 0}</span></p>
        <p style="margin: 0; font-size: 12px; color: #9ca3af;">Riesgo Simulado: <span class="${riesgo.textClass}" style="font-weight: bold;">${riesgo.texto}</span></p>
        <p style="margin: 0; font-size: 10px; color: #9ca3af; margin-top: 4px;">Índice Ocup.: <span style="color: ${props.PRO_OCUP_C >= 1.5 ? '#ef4444' : '#4ade80'};">${props.PRO_OCUP_C ? Number(props.PRO_OCUP_C).toFixed(1) : '1.0'}</span></p>
        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #1f402d;"><p style="margin: 0; font-size: 9px; color: #4ade80; text-align: center;">Clic para Análisis de IA Completo</p></div>
      </div>
    `;

    layer.bindTooltip(tooltipContent, { sticky: true, className: 'custom-leaflet-tooltip' });

    layer.on({
      mouseover: (e) => { e.target.setStyle({ weight: 3, fillOpacity: 0.8, color: '#ffffff' }); e.target.bringToFront(); },
      mouseout: (e) => { e.target.setStyle(estiloManzana(feature)); },
      click: async (e) => {
        const lat = e.latlng.lat; const lon = e.latlng.lng;
        setSelectedManzana({ ...props, lat, lon, cargando: true });
        try {
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`);
          const data = await res.json();
          const addr = data.address || {};
          const colonia = addr.neighbourhood || addr.suburb || addr.residential || 'Colonia no especificada';
          const cp = addr.postcode || 'S/N';
          const calle = addr.road || 'Calle principal';
          setSelectedManzana({ ...props, lat, lon, colonia, cp, calle, riesgoTexto: riesgo.texto, cargando: false });
        } catch (error) {
          setSelectedManzana({ ...props, lat, lon, colonia: 'Error de red', cp: 'N/A', calle: 'N/A', cargando: false });
        }
      }
    });
  };

  if (!geoData) return null;
  return <GeoJSON key={`${simulador.activo}-${simulador.temp}-${filtroRiesgo}-${mapStyle}`} data={geoData} style={estiloManzana} onEachFeature={onEachManzana} />;
}