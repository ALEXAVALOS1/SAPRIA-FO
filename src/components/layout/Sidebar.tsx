import React, { useState, useRef } from 'react';

// Añadimos onCloseMobile a la interfaz
interface SidebarProps {
  layers: any; setLayers: any;
  clima: any; calidadAire: any;
  onSearch: any;
  filtroRiesgo: string; setFiltroRiesgo: any;
  simulador: any; setSimulador: any;
  mapStyle: string; setMapStyle: any;
  onCloseMobile?: () => void;
}

export default function Sidebar({
  layers, setLayers, clima, calidadAire, onSearch,
  filtroRiesgo, setFiltroRiesgo, simulador, setSimulador,
  mapStyle, setMapStyle, onCloseMobile
}: SidebarProps) {

  const [localSearch, setLocalSearch] = useState('');
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeout = useRef<any>(null);

  const toggleLayer = (layerName: string) => setLayers((prev: any) => ({ ...prev, [layerName]: !prev[layerName] }));
  const toggleSimulador = () => setSimulador((prev: any) => ({ ...prev, activo: !prev.activo }));

  const handleSearchInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setLocalSearch(val);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    if (val.length > 3) {
      setIsSearching(true);
      searchTimeout.current = setTimeout(async () => {
        try {
          const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(val)}+Ciudad+Juarez&limit=5`);
          setSuggestions(await res.json());
        } catch (error) { console.error(error); } 
        finally { setIsSearching(false); }
      }, 500);
    } else setSuggestions([]);
  };

  const handleSelectSuggestion = (sug: any) => {
    setLocalSearch(sug.name || sug.display_name.split(',')[0]);
    setSuggestions([]);
    onSearch([parseFloat(sug.lat), parseFloat(sug.lon)]);
    if(onCloseMobile) onCloseMobile(); // Cierra el menú al buscar en móvil
  };

  return (
    <aside className="w-full h-full bg-[#0a150f] border-r border-[#1a3324] flex flex-col shadow-2xl relative z-20">
      
      <div className="p-6 pb-2 flex justify-between items-start">
        <div>
          <h2 className="text-white font-black text-lg">Capas de Monitoreo</h2>
          <p className="text-gray-400 text-xs mt-1">Zona: Ciudad Juárez</p>
        </div>
        {/* BOTÓN CERRAR MÓVIL */}
        {onCloseMobile && (
          <button onClick={onCloseMobile} className="lg:hidden text-gray-500 hover:text-white text-2xl font-black bg-[#11241a] w-8 h-8 rounded-md flex items-center justify-center border border-[#1f402d]">
            ×
          </button>
        )}
      </div>

      <div className="p-6 flex-1 overflow-y-auto custom-scrollbar space-y-6">
        
        <div className="relative">
          <span className="absolute left-3 top-2.5 text-gray-500">🔍</span>
          <input type="text" value={localSearch} onChange={handleSearchInput} placeholder="Escribe colonia o calle..." className="w-full bg-[#11241a] border border-[#1f402d] rounded-lg py-2 pl-9 pr-8 text-sm text-white focus:outline-none focus:border-emerald-500" />
          {isSearching && <span className="absolute right-3 top-2.5 text-emerald-500 animate-pulse text-xs">...</span>}
          {suggestions.length > 0 && (
            <ul className="absolute top-full left-0 w-full mt-1 bg-[#11241a] border border-[#1f402d] rounded-lg shadow-2xl z-50 max-h-48 overflow-y-auto custom-scrollbar">
              {suggestions.map((sug, idx) => (
                <li key={idx} onClick={() => handleSelectSuggestion(sug)} className="px-4 py-2 hover:bg-[#1a3324] cursor-pointer text-xs border-b border-[#1f402d] transition-colors">
                  <strong className="text-emerald-400 block">{sug.name || sug.display_name.split(',')[0]}</strong>
                  <span className="text-[9px] text-gray-500 truncate block">{sug.display_name}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[9px] text-gray-500 uppercase tracking-widest font-bold mb-1 block">Estilo</label>
            <select value={mapStyle} onChange={(e) => setMapStyle(e.target.value)} className="w-full bg-[#11241a] border border-[#1f402d] rounded text-xs text-white p-2 focus:outline-none">
              <option value="dark">Táctico</option>
              <option value="satellite">Satélite</option>
              <option value="light">Claro</option>
            </select>
          </div>
          <div>
            <label className="text-[9px] text-gray-500 uppercase tracking-widest font-bold mb-1 block">Radar IA</label>
            <select value={filtroRiesgo} onChange={(e) => setFiltroRiesgo(e.target.value)} className="w-full bg-[#11241a] border border-[#1f402d] rounded text-xs text-white p-2 focus:outline-none">
              <option value="TODOS">Mostrar Todas</option>
              <option value="CRITICOS">Solo Críticas</option>
            </select>
          </div>
        </div>

        <div>
          <label className="text-[9px] text-gray-500 uppercase tracking-widest font-bold mb-3 block">Visualización</label>
          <div className="space-y-4">
            <div className="flex justify-between items-center cursor-pointer" onClick={() => toggleLayer('manzanas')}>
              <span className="text-sm text-gray-200 font-bold">Polígonos Urbanos</span>
              <div className={`w-8 h-4 rounded-full relative transition-colors ${layers.manzanas ? 'bg-emerald-500' : 'bg-[#1f402d]'}`}>
                <div className={`w-4 h-4 bg-white rounded-full absolute transition-transform ${layers.manzanas ? 'right-0' : 'left-0 bg-gray-400'}`}></div>
              </div>
            </div>
            <div className="flex justify-between items-center cursor-pointer" onClick={() => toggleLayer('unidades')}>
              <span className="text-sm text-gray-200 font-bold">Unidades Respuesta</span>
              <div className={`w-8 h-4 rounded-full relative transition-colors ${layers.unidades ? 'bg-blue-500' : 'bg-[#1f402d]'}`}>
                <div className={`w-4 h-4 bg-white rounded-full absolute transition-transform ${layers.unidades ? 'right-0' : 'left-0 bg-gray-400'}`}></div>
              </div>
            </div>
            <div className="flex justify-between items-center cursor-pointer" onClick={() => toggleLayer('mapas_calor')}>
              <span className="text-sm text-gray-200 font-bold">Mapas de Calor</span>
              <div className={`w-8 h-4 rounded-full relative transition-colors ${layers.mapas_calor ? 'bg-orange-500' : 'bg-[#1f402d]'}`}>
                <div className={`w-4 h-4 bg-white rounded-full absolute transition-transform ${layers.mapas_calor ? 'right-0' : 'left-0 bg-gray-400'}`}></div>
              </div>
            </div>
            <div className="flex justify-between items-center cursor-pointer" onClick={() => toggleLayer('historial')}>
              <span className="text-sm text-gray-200 font-bold">Historial Riesgos</span>
              <div className={`w-8 h-4 rounded-full relative transition-colors ${layers.historial ? 'bg-purple-500' : 'bg-[#1f402d]'}`}>
                <div className={`w-4 h-4 bg-white rounded-full absolute transition-transform ${layers.historial ? 'right-0' : 'left-0 bg-gray-400'}`}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-[#1a3324] bg-[#0a150f]">
        <div className="flex justify-between items-center mb-3">
          <span className="text-[9px] text-gray-500 uppercase tracking-widest font-bold">Modo Operativo</span>
          <button onClick={toggleSimulador} className={`text-[9px] font-bold px-2 py-1 rounded border flex items-center gap-1 transition-all ${simulador.activo ? 'text-orange-400 border-orange-800 bg-orange-900/30' : 'text-emerald-400 border-emerald-800 bg-emerald-900/30 hover:bg-emerald-900/50'}`}>
            {simulador.activo ? '⚙️ Simulación' : '🧪 Clima en Vivo'}
          </button>
        </div>

        {simulador.activo ? (
          <div className="space-y-3 h-48 overflow-y-auto custom-scrollbar pr-1">
            <div className="bg-[#11241a] p-2 rounded border border-[#1f402d]">
              <div className="flex justify-between text-[10px] mb-2"><span className="text-gray-400">Temperatura</span><span className="text-orange-400 font-bold">{simulador.temp}°C</span></div>
              <input type="range" min="10" max="50" value={simulador.temp} onChange={(e) => setSimulador({...simulador, temp: Number(e.target.value)})} className="w-full h-1 bg-gray-800 rounded-lg accent-orange-500" />
            </div>
            <div className="bg-[#11241a] p-2 rounded border border-[#1f402d]">
              <div className="flex justify-between text-[10px] mb-2"><span className="text-gray-400">Viento</span><span className="text-blue-400 font-bold">{simulador.viento} km/h</span></div>
              <input type="range" min="0" max="80" value={simulador.viento} onChange={(e) => setSimulador({...simulador, viento: Number(e.target.value)})} className="w-full h-1 bg-gray-800 rounded-lg accent-blue-500" />
            </div>
            <div className="bg-[#11241a] p-2 rounded border border-[#1f402d]">
              <div className="flex justify-between text-[10px] mb-2"><span className="text-gray-400">Humedad</span><span className="text-blue-300 font-bold">{simulador.humedad}% 💧</span></div>
              <input type="range" min="0" max="100" value={simulador.humedad} onChange={(e) => setSimulador({...simulador, humedad: Number(e.target.value)})} className="w-full h-1 bg-gray-800 rounded-lg accent-blue-300" />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-[#11241a] p-2 rounded border border-[#1f402d]">
              <span className="text-[9px] text-gray-500 block mb-1">Temp / Viento</span>
              <span className="text-lg font-black text-white block leading-none mb-1">{clima?.main?.temp || '36'}°C</span>
              <span className="text-[9px] text-blue-400">💨 {clima?.wind?.speed || '6.5'} km/h</span>
            </div>
            <div className="bg-[#11241a] p-2 rounded border border-[#1f402d]">
              <span className="text-[9px] text-gray-500 block mb-1">Humedad / Aire</span>
              <span className="text-lg font-black text-blue-400 block leading-none mb-1">{clima?.main?.humidity || '15'}% 💧</span>
              <span className="text-[9px] text-yellow-500">AQI: {calidadAire || 2}/5</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}