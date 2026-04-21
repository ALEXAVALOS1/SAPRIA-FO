export interface Estacion {
  nombre: string;
  direccion: string;
  lat: number;
  lon: number;
}

export interface Analitica {
  tendencias: any[];
  escenario_inaccion: {
    incidentes_proyectados: number;
    total_historico: number;
  };
  importancia: any[];
}