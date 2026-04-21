import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useEffect, useState } from 'react';

export default function NeighborhoodRanking() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('./data/ranking_zonas_calientes.json')
      .then(r => r.json())
      .then(setData);
  }, []);

  return (
    <div className="bg-[#4a5568] p-10 rounded-[45px] border border-slate-500 shadow-2xl h-[400px]">
      <h3 className="text-[#D4AF37] text-xs font-black uppercase tracking-widest mb-10 text-center">
        Top 10: Sectores con Mayor Incidencia de Incendios (Histórico Real)
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical">
          <XAxis type="number" hide />
          <YAxis dataKey="lat_round" type="category" stroke="#cbd5e0" fontSize={10} width={80} />
          <Tooltip cursor={{fill: '#2d3748'}} contentStyle={{backgroundColor: '#2d3748', border: 'none', borderRadius: '10px'}} />
          <Bar dataKey="conteo" name="Incendios" fill="#D4AF37" radius={[0, 10, 10, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}