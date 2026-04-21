import React, { useState, useEffect } from 'react';
import { generarReporteTactico } from '../../utils/reportGenerator';

interface TopBarProps {
  selectedManzana: any;
  simulador: { activo: boolean; temp: number; viento: number };
}

export default function TopBar({ selectedManzana, simulador }: TopBarProps) {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const isExtremeWeather = simulador.activo && (simulador.temp >= 38 || simulador.viento >= 40);

  return (
    <header className={`h-16 flex items-center justify-between px-4 md:px-6 border-b transition-colors duration-500 z-10 shadow-md ${
      isExtremeWeather ? 'bg-red-950/80 border-red-500/50' : 'bg-[#0a1710] border-[#1f402d]'
    }`}>
      
      <div className="flex items-center gap-3 md:gap-4">
        <div className={`w-8 h-8 md:w-10 md:h-10 rounded-lg flex items-center justify-center border transition-colors duration-500 ${
          isExtremeWeather ? 'bg-red-900 border-red-500 text-red-300' : 'bg-[#112a1c] border-emerald-800 text-emerald-500'
        }`}>
          <span className="text-lg md:text-xl font-black">🔥</span>
        </div>
        <div>
          <h1 className="text-white font-black tracking-widest text-md md:text-lg leading-none">URBIPREX</h1>
          <p className="text-[8px] md:text-[10px] uppercase tracking-widest font-bold text-emerald-600 hidden sm:block">
            Protección Civil Municipal
          </p>
        </div>
      </div>

      <div className="flex-1 flex justify-center">
        {isExtremeWeather ? (
          <div className="flex items-center gap-2 md:gap-3 bg-red-600/20 px-3 md:px-6 py-1 md:py-1.5 rounded-full border border-red-500 animate-pulse">
            <span className="text-red-500 text-sm md:text-lg">🚨</span>
            <span className="text-red-300 font-bold tracking-widest text-[9px] md:text-xs uppercase hidden md:inline">Alerta de Propagación</span>
          </div>
        ) : simulador.activo ? (
          <div className="flex items-center gap-2 md:gap-3 bg-orange-900/30 px-3 md:px-6 py-1 md:py-1.5 rounded-full border border-orange-700/50">
            <span className="text-orange-500 text-sm md:text-lg">🌤️</span>
            <span className="text-orange-300 font-bold tracking-widest text-[9px] md:text-xs uppercase hidden md:inline">Simulación Activa</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 md:gap-3 bg-[#112a1c] px-3 md:px-6 py-1 md:py-1.5 rounded-full border border-[#1f402d]">
            <span className="text-emerald-500 text-sm md:text-lg">📡</span>
            <span className="text-gray-400 font-bold tracking-widest text-[9px] md:text-xs uppercase hidden md:inline">Monitoreo Estructural Normal</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 md:gap-6">
        <div className="text-right hidden lg:block">
          <p className="text-white font-mono font-bold text-sm">
            {time.toLocaleTimeString('es-MX', { hour12: false })} HRS
          </p>
          <p className="text-gray-500 text-[10px] tracking-widest uppercase">
            {time.toLocaleDateString('es-MX')}
          </p>
        </div>
        
        <button 
          onClick={() => generarReporteTactico(selectedManzana, simulador)}
          className={`px-3 md:px-4 py-2 rounded font-bold text-[10px] md:text-xs tracking-widest uppercase transition-all flex items-center gap-2 ${
            !selectedManzana 
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700'
              : 'bg-white hover:bg-gray-200 text-[#0a1710] shadow-[0_0_15px_rgba(255,255,255,0.2)]'
          }`}
          disabled={!selectedManzana}
        >
          📄 <span className="hidden sm:inline">Generar Reporte</span>
        </button>
      </div>
    </header>
  );
}