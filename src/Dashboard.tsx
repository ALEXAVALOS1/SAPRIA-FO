import React, { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import MapSection from './components/MapSection';
import RightPanel from './components/RightPanel';

export default function Dashboard() {
  const [layers, setLayers] = useState({ manzanas: true, unidades: true, mapas_calor: false, historial: false });
  const [filtroRiesgo, setFiltroRiesgo] = useState('TODOS');
  const [simulador, setSimulador] = useState({ activo: false, temp: 36, viento: 20, humedad: 30, trafico: 50 });
  const [selectedManzana, setSelectedManzana] = useState<any>(null);
  const [mapStyle, setMapStyle] = useState('dark');
  const [searchPos, setSearchPos] = useState<[number, number] | null>(null);
  
  const [weather, setWeather] = useState<any>(null);
  const [calidadAire, setCalidadAire] = useState<number | null>(null);

  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  const [showMobileRightPanel, setShowMobileRightPanel] = useState(false);

  useEffect(() => {
    setWeather({ main: { temp: 36, humidity: 15 }, wind: { speed: 6.5 } });
    setCalidadAire(2);
  }, []);

  const handleSelectManzana = (manzana: any) => {
    setSelectedManzana(manzana);
    if (manzana) setShowMobileRightPanel(true);
  };

  return (
    <div className="flex flex-col h-screen bg-[#0b1c14] text-white font-sans overflow-hidden">
      <TopBar selectedManzana={selectedManzana} simulador={simulador} />
      
      <main className="flex-1 flex p-0 lg:p-4 gap-0 lg:gap-4 overflow-hidden relative">
        
        {/* 📱 BOTONES FLOTANTES MÓVILES (HUD Táctico Institucional) */}
        <button 
          onClick={() => setShowMobileSidebar(true)} 
          className="absolute top-4 left-4 z-30 lg:hidden bg-[#0a150f]/95 border border-[#1f402d] px-4 py-2.5 rounded-lg shadow-[0_4px_20px_rgba(0,0,0,0.8)] backdrop-blur-md flex items-center gap-2 hover:bg-[#11241a] transition-all"
        >
          {/* Icono Menu Profesional */}
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <span className="text-[10px] font-bold tracking-widest text-gray-300 uppercase">Control</span>
        </button>

        <button 
          onClick={() => setShowMobileRightPanel(true)} 
          className="absolute top-4 right-4 z-30 lg:hidden bg-[#0a150f]/95 border border-emerald-900/60 px-4 py-2.5 rounded-lg shadow-[0_4px_20px_rgba(0,0,0,0.8)] backdrop-blur-md flex items-center gap-2 hover:bg-[#11241a] transition-all"
        >
          {/* Icono Chip/IA Táctico */}
          <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          <span className="text-[10px] font-bold tracking-widest text-emerald-500 uppercase">Radar IA</span>
        </button>

        {/* 📱 FONDO OSCURO PARA CERRAR SIDEBAR MÓVIL */}
        {showMobileSidebar && <div className="fixed inset-0 bg-black/80 z-40 lg:hidden backdrop-blur-sm" onClick={() => setShowMobileSidebar(false)}></div>}

        {/* PANEL IZQUIERDO */}
        <div className={`absolute lg:relative top-0 left-0 h-full w-80 flex-shrink-0 z-50 transform transition-transform duration-300 ease-in-out ${showMobileSidebar ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
          <Sidebar 
            layers={layers} setLayers={setLayers}
            clima={weather} calidadAire={calidadAire}
            onSearch={setSearchPos}
            filtroRiesgo={filtroRiesgo} setFiltroRiesgo={setFiltroRiesgo}
            simulador={simulador} setSimulador={setSimulador}
            mapStyle={mapStyle} setMapStyle={setMapStyle}
            onCloseMobile={() => setShowMobileSidebar(false)}
          />
        </div>

        {/* MAPA CENTRAL */}
        <div className="flex-1 h-full w-full lg:rounded-2xl overflow-hidden border-y lg:border border-[#1f402d] shadow-2xl relative z-0">
          <MapSection 
            searchPos={searchPos} layers={layers} filtroRiesgo={filtroRiesgo}
            simulador={simulador} setSelectedManzana={handleSelectManzana}
            selectedManzana={selectedManzana} mapStyle={mapStyle}
          />
        </div>

        {/* 📱 FONDO OSCURO PARA CERRAR PANEL IA MÓVIL */}
        {showMobileRightPanel && <div className="fixed inset-0 bg-black/80 z-40 lg:hidden backdrop-blur-sm" onClick={() => setShowMobileRightPanel(false)}></div>}

        {/* PANEL DERECHO (IA) */}
        <div className={`absolute lg:relative top-0 right-0 h-full w-80 flex-shrink-0 z-50 transform transition-transform duration-300 ease-in-out ${showMobileRightPanel ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}`}>
          <RightPanel weather={weather} simulador={simulador} selectedManzana={selectedManzana} onCloseMobile={() => setShowMobileRightPanel(false)} />
        </div>

      </main>
    </div>
  );
}