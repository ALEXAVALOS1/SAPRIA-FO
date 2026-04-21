import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function AdvancedTrends({ clima }: { clima: any }) {
  const [realStats, setRealStats] = useState<any>(null);

  useEffect(() => {
    fetch('./data/analitica_historia.json')
      .then(r => r.json())
      .then(setRealStats)
      .catch(e => console.error("No hay datos históricos reales aún"));
  }, []);

  if (!realStats) return <div className="p-10 text-slate-500">Cargando base de datos real...</div>;

  return (
    <div className="p-8 space-y-8 bg-[#2d3748] h-full overflow-y-auto">
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-[#4a5568] p-6 rounded-3xl border border-slate-500 shadow-xl">
          <p className="text-[10px] text-[#D4AF37] font-black uppercase mb-2">Total Histórico</p>
          <p className="text-3xl font-black text-white">{realStats.total_registros}</p>
          <p className="text-[10px] text-slate-400 mt-1 font-bold">Eventos registrados en incendios.csv</p>
        </div>
        <div className="bg-[#4a5568] p-6 rounded-3xl border border-slate-500 shadow-xl">
          <p className="text-[10px] text-red-400 font-black uppercase mb-2">Promedio Diario</p>
          <p className="text-3xl font-black text-white">{realStats.promedio_diario}</p>
          <p className="text-[10px] text-slate-400 mt-1 font-bold">Detecciones térmicas/día</p>
        </div>
        <div className="bg-[#4a5568] p-6 rounded-3xl border border-slate-500 shadow-xl">
          <p className="text-[10px] text-blue-400 font-black uppercase mb-2">FWI Actual</p>
          <p className="text-3xl font-black text-white">{clima.fwi}%</p>
        </div>
      </div>

      <div className="bg-[#4a5568] p-10 rounded-[40px] border border-slate-500 shadow-2xl">
        <h3 className="text-[#D4AF37] text-xs font-black uppercase tracking-widest mb-10">Tendencia Mensual Extraída de Base de Datos</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={realStats.mensual}>
              <CartesianGrid strokeDasharray="3 3" stroke="#718096" vertical={false} />
              <XAxis dataKey="acq_date" stroke="#cbd5e0" fontSize={12} />
              <YAxis stroke="#cbd5e0" fontSize={12} />
              <Tooltip contentStyle={{backgroundColor: '#2d3748', border: '1px solid #D4AF37', borderRadius: '15px'}} />
              <Area type="monotone" dataKey="v" stroke="#D4AF37" fill="#D4AF37" fillOpacity={0.1} strokeWidth={4} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}