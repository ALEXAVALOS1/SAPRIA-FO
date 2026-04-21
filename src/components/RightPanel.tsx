import React, { useState, useEffect } from 'react';

// Añadimos onCloseMobile a la interfaz
interface RightPanelProps {
  weather: any;
  simulador: any;
  selectedManzana: any;
  onCloseMobile?: () => void;
}

export default function RightPanel({ weather, simulador, selectedManzana, onCloseMobile }: RightPanelProps) {
  const [prediccionIA, setPrediccionIA] = useState<any>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [errorIA, setErrorIA] = useState<string | null>(null);

  const tempActual = simulador?.activo ? simulador.temp : (weather?.main?.temp || 25);
  const vientoActual = simulador?.activo ? simulador.viento : (weather?.wind?.speed || 10);

  useEffect(() => {
    if (!selectedManzana) {
      setPrediccionIA(null);
      setErrorIA(null);
      return;
    }

    const consultarCerebroIA = async () => {
      setIsPredicting(true);
      setErrorIA(null);
      try {
        const payload = {
          distancia_bomberos_m: selectedManzana.distancia_bomberos_m || 3500,
          poblacion_total: selectedManzana.poblacion_total || selectedManzana.POBTOT || 0,
          densidad_vial: selectedManzana.densidad_vial || 0,
          temp: tempActual,
          viento: vientoActual,
          tipo_zona_calculada: selectedManzana.tipo_zona_calculada || 1,
          PRO_OCUP_C: selectedManzana.PRO_OCUP_C || 1.0
        };

        const response = await fetch('http://127.0.0.1:8000/predecir', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Servidor IA no responde");
        setPrediccionIA(await response.json());
      } catch (error) {
        setErrorIA("Conexión perdida con servidor Python.");
      } finally {
        setIsPredicting(false);
      }
    };
    consultarCerebroIA();
  }, [selectedManzana, tempActual, vientoActual]);

  if (!selectedManzana) {
    return (
      <aside className="w-full h-full bg-[#0a150f] border-l border-[#1a3324] flex flex-col items-center justify-center p-6 shadow-2xl relative z-20">
        {onCloseMobile && (
          <button onClick={onCloseMobile} className="absolute top-4 right-4 lg:hidden text-gray-500 hover:text-white text-2xl font-black bg-[#11241a] w-8 h-8 rounded-md flex items-center justify-center border border-[#1f402d]">
            ×
          </button>
        )}
        <img src="/URBIPREX - LOGO GITHUB.PNG" alt="URBIPREX" className="h-16 w-auto object-contain mb-8 opacity-50" onError={(e) => e.currentTarget.style.display = 'none'} />
        <div className="relative flex items-center justify-center mb-6">
          <div className="absolute w-24 h-24 border border-emerald-500/30 rounded-full animate-ping"></div>
          <div className="absolute w-16 h-16 border border-emerald-500/50 rounded-full animate-spin" style={{ animationDuration: '3s' }}></div>
          <div className="w-4 h-4 bg-emerald-500 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.8)]"></div>
        </div>
        <h3 className="text-emerald-500 font-bold tracking-widest text-sm mb-2 text-center uppercase">Radar Global Activo</h3>
        <p className="text-center text-xs text-gray-500">Monitoreando la ciudad. Selecciona una zona en el mapa para analizar el riesgo.</p>
      </aside>
    );
  }

  const prob = prediccionIA?.probabilidad_incendio || 0;
  const esCritico = prob > 0.65;
  const esAlto = prob > 0.40 && prob <= 0.65;
  
  let colorRiesgo = "text-emerald-400"; let bgRiesgo = "bg-emerald-900/30 border-emerald-800"; let textoRiesgo = "BAJO / MEDIO";
  if (esCritico) { colorRiesgo = "text-red-500"; bgRiesgo = "bg-red-900/30 border-red-800"; textoRiesgo = "CRÍTICO"; } 
  else if (esAlto) { colorRiesgo = "text-orange-500"; bgRiesgo = "bg-orange-900/30 border-orange-800"; textoRiesgo = "ALTO"; }

  const tipoZonaCodigo = selectedManzana.tipo_zona_calculada || 1;
  let tipoZonaTexto = "Baldío / Parque / Lote"; let colorZona = "text-gray-400";
  if (tipoZonaCodigo === 2) { tipoZonaTexto = "Residencial / Vivienda"; colorZona = "text-amber-400"; } 
  else if (tipoZonaCodigo === 3) { tipoZonaTexto = "Comercial / Industrial"; colorZona = "text-purple-400"; }

  const hacinamiento = selectedManzana.PRO_OCUP_C || 1.0;
  let colorHacinamiento = "text-emerald-400"; let textoHacinamiento = "Normal (Bajo Riesgo)";
  if (hacinamiento > 2.0) { colorHacinamiento = "text-red-400"; textoHacinamiento = "ALTO (Peligro Eléctrico)"; } 
  else if (hacinamiento > 1.2) { colorHacinamiento = "text-amber-400"; textoHacinamiento = "MODERADO"; }

  return (
    <aside className="w-full h-full bg-[#0a150f] border-l border-[#1a3324] flex flex-col shadow-2xl relative z-20 overflow-y-auto custom-scrollbar">
      
      <div className="flex flex-col items-center justify-center p-4 border-b border-[#1f402d] bg-[#11241a] shadow-inner relative">
        {/* BOTÓN CERRAR MÓVIL */}
        {onCloseMobile && (
          <button onClick={onCloseMobile} className="absolute top-4 right-4 lg:hidden text-gray-500 hover:text-white text-2xl font-black bg-[#0a150f] w-8 h-8 rounded-md flex items-center justify-center border border-[#1f402d]">
            ×
          </button>
        )}
        <img src="/URBIPREX - LOGO GITHUB.PNG" alt="URBIPREX" className="h-16 w-auto object-contain mb-2 rounded-lg" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
        <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest font-mono">Powered by AI - V4</span>
      </div>

      <div className="p-4 border-b border-[#1a3324]">
        <h2 className="text-white font-black tracking-widest uppercase text-xs mb-1">Análisis de Sector</h2>
        <p className="text-[10px] text-gray-400 font-mono">Código de Zona: {selectedManzana.CVEGEO || 'N/A'}</p>
      </div>

      <div className="p-4 space-y-4">
        {errorIA && <div className="bg-red-900/30 border border-red-800 p-3 rounded-lg"><p className="text-xs text-red-400">{errorIA}</p></div>}
        
        <div className={`p-4 rounded-lg border ${bgRiesgo} transition-colors duration-500 relative overflow-hidden`}>
          {isPredicting && <div className="absolute inset-0 bg-[#0a150f]/90 flex items-center justify-center z-10"><span className="text-emerald-500 text-xs font-bold animate-pulse">Calculando...</span></div>}
          <h3 className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2 flex items-center gap-2"><span className="text-blue-400">🧠</span> Modelo V4</h3>
          <div className="flex justify-between items-end mb-1"><span className="text-xs font-bold text-gray-300">Riesgo:</span><span className={`text-lg font-black ${colorRiesgo}`}>{textoRiesgo}</span></div>
          <div className="flex justify-between items-end"><span className="text-[10px] text-gray-500">Probabilidad:</span><span className={`text-3xl font-black tracking-tighter ${colorRiesgo}`}>{prediccionIA ? prediccionIA.porcentaje_visual : '--%'}</span></div>
        </div>

        <div className="bg-[#11241a] p-3 rounded-lg border border-[#1f402d] flex flex-col gap-1">
          <div className="flex justify-between items-center"><span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Suelo:</span><span className={`text-xs font-black ${colorZona}`}>{tipoZonaTexto}</span></div>
          <div className="flex justify-between items-center mt-2 pt-2 border-t border-[#1a3324]"><span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Viviendas:</span><span className={`text-xs font-black ${colorHacinamiento}`}>{textoHacinamiento}</span></div>
        </div>

        <div className="bg-[#11241a] p-4 rounded-lg border border-[#1f402d]">
          <h3 className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-3">Recomendación</h3>
          <p className="text-xs text-gray-300 leading-relaxed">{esCritico ? "🚨 ALERTA MÁXIMA: Peligro de sobrecarga eléctrica." : esAlto ? "⚠️ PRECAUCIÓN: Zona vulnerable." : "✅ ZONA SEGURA."}</p>
        </div>

        <div>
          <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-3 border-b border-[#1f402d] pb-1">Datos Leídos</h3>
          <ul className="space-y-3">
            <li className="flex justify-between"><span className="text-xs text-gray-400">Distancia a Bomberos</span><span className="text-xs font-bold text-white">{selectedManzana.distancia_bomberos_m ? `${Math.round(selectedManzana.distancia_bomberos_m)} mts` : 'N/D'}</span></li>
            <li className="flex justify-between"><span className="text-xs text-gray-400">Población</span><span className="text-xs font-bold text-white">{selectedManzana.poblacion_total || selectedManzana.POBTOT || 0} personas</span></li>
            <li className="flex justify-between mt-2 pt-2 border-t border-[#1a3324]"><span className="text-xs text-orange-400/80">Temperatura</span><span className="text-xs font-bold text-orange-400">{tempActual}°C</span></li>
            <li className="flex justify-between"><span className="text-xs text-blue-400/80">Viento</span><span className="text-xs font-bold text-blue-400">{vientoActual} km/h</span></li>
          </ul>
        </div>
      </div>
    </aside>
  );
}