import { useEffect, useState } from 'react';

export default function SegmentAnalysis({ factor, viento }: any) {
  const [datos, setDatos] = useState<any>(null);

  useEffect(() => {
    fetch('./data/analitica_real.json').then(r => r.json()).then(setDatos).catch(() => {});
  }, []);

  if (!datos) return <div className="p-20 text-[#FACC15] font-black animate-pulse uppercase tracking-[0.5em]">CARGANDO INTELIGENCIA JUÁREZ...</div>;

  const totalSimulado = Math.round(datos.escenario_inaccion.proyectados * factor);

  return (
    <div className="max-w-7xl mx-auto space-y-12">
      {/* 🌪️ PANEL DE IMPACTO DINÁMICO */}
      <div className={`p-12 rounded-[50px] border transition-all duration-700 relative overflow-hidden ${viento > 40 ? 'bg-red-600/20 border-red-500 shadow-[0_0_50px_rgba(239,68,68,0.2)]' : 'bg-white/5 border-white/10'}`}>
        <div className="scan-line opacity-40"></div>
        <h3 className="text-red-500 font-black text-xs uppercase tracking-widest mb-4 italic">Proyección de Riesgo (Simulación {viento}km/h)</h3>
        <p className="text-white text-8xl font-black tracking-tighter leading-none">{totalSimulado}</p>
        <p className="text-slate-500 text-[10px] font-bold uppercase mt-6 tracking-widest leading-relaxed">
          Siniestros adicionales proyectados basados en ráfagas actuales y recurrencia histórica de {datos.escenario_inaccion.historicos} incidentes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* INDICADORES INEGI POR SECTOR */}
        <div className="glass p-10 rounded-[50px]">
          <h2 className="text-[#FACC15] font-black text-xl mb-10 uppercase tracking-tighter italic">Vulnerabilidad de Población (INEGI)</h2>
          <div className="space-y-6">
            {datos.sectores.map((s:any, i:number) => (
              <div key={i} className="bg-white/5 p-8 rounded-[40px] border border-white/5 hover:border-[#FACC15]/30 transition-all">
                <div className="flex justify-between items-center mb-6">
                  <h4 className="text-white text-base font-black uppercase tracking-tight">{s.nombre}</h4>
                  <span className="text-red-500 font-black text-[10px] border border-red-500/20 px-4 py-1 rounded-full uppercase italic">{s.rezago} REZAGO</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="border-l-2 border-[#FACC15]/30 pl-4">
                    <p className="text-[9px] text-slate-500 font-black uppercase">Ciudadanos</p>
                    <p className="text-white text-2xl font-black italic">{s.pob.toLocaleString()}</p>
                  </div>
                  <div className="border-l-2 border-slate-700 pl-4 text-right">
                    <p className="text-[9px] text-slate-500 font-black uppercase">Servicios</p>
                    <p className="text-white text-2xl font-black italic">{s.inc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* MATRIZ DE RIESGO E HIDRANTES */}
        <div className="glass p-10 rounded-[50px] flex flex-col">
          <h2 className="text-white font-black text-xl mb-10 uppercase tracking-tighter italic">Factores de Ignición Dominantes</h2>
          <div className="flex-1 space-y-10">
            {datos.factores.map((f:any, i:number) => (
              <div key={i} className="group">
                <div className="flex justify-between text-[11px] text-slate-400 mb-2 font-black uppercase tracking-widest italic group-hover:text-white transition-all">
                  <span>{f.name}</span><span>{f.value}%</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                  <div className="h-full shadow-[0_0_15px_#FACC15] transition-all duration-[2000ms]" style={{ width: `${f.value}%`, backgroundColor: f.color }}></div>
                </div>
              </div>
            ))}
            
            <div className="mt-10 p-10 bg-[#FACC15]/10 border border-[#FACC15]/20 rounded-[45px] flex items-center justify-between group hover:bg-[#FACC15]/20 transition-all">
               <div>
                 <p className="text-cyan-400 font-black text-[10px] uppercase tracking-[0.2em] mb-1">Apoyo Hidráulico (JMAS)</p>
                 <p className="text-white text-3xl font-black italic uppercase">Operativo</p>
               </div>
               <div className="text-5xl group-hover:rotate-12 transition-transform duration-500">🚰</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}