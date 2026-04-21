import { Polygon, Tooltip } from 'react-leaflet';

interface SimulationProps {
  startPoint: [number, number];
  windDir: number; // Grados (0-360)
  windVel: number; // m/s
}

export default function SimulationLayer({ startPoint, windDir, windVel }: SimulationProps) {
  if (!startPoint) return null;

  // El fuego avanza más rápido y más ancho con más viento
  const distance = (windVel * 0.005); // Factor de alcance
  const spread = 30 + (windVel * 2);  // Ángulo de apertura del cono

  // Convertir dirección de grados a radianes (Ajuste para coordenadas de mapa)
  const angleRad = (windDir - 90) * (Math.PI / 180);
  const leftAngle = angleRad - (spread * Math.PI / 180 / 2);
  const rightAngle = angleRad + (spread * Math.PI / 180 / 2);

  // Calcular puntos del polígono de riesgo
  const point1: [number, number] = [
    startPoint[0] - Math.sin(leftAngle) * distance,
    startPoint[1] + Math.cos(leftAngle) * distance
  ];
  const point2: [number, number] = [
    startPoint[0] - Math.sin(rightAngle) * distance,
    startPoint[1] + Math.cos(rightAngle) * distance
  ];

  const polygonPoints: [number, number][] = [startPoint, point1, point2];

  return (
    <Polygon 
      positions={polygonPoints}
      pathOptions={{
        fillColor: '#D4AF37',
        color: '#D4AF37',
        weight: 2,
        fillOpacity: 0.4,
        dashArray: '5, 10'
      }}
    >
      <Tooltip sticky>Área de Dispersión Probable (Viento: {windVel} m/s)</Tooltip>
    </Polygon>
  );
}