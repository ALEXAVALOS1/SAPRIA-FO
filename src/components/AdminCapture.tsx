import React, { useState } from 'react';

interface AdminCaptureProps {
  onBackToDashboard: () => void;
}

export default function AdminCapture({ onBackToDashboard }: AdminCaptureProps) {
  const [ubicacion, setUbicacion] = useState<{lat: number, lon: number} | null>(null);
  const [cargandoGPS, setCargandoGPS] = useState(false);
  const [tipo, setTipo] = useState('falla_electrica');
  const [severidad, setSeveridad] = useState('1');
  const [notas, setNotas] = useState('');
  const [enviado, setEnviado] = useState(false);

  const capturarGPS = () => {
    setCargandoGPS(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (p) => {
          setUbicacion({ lat: p.coords.latitude, lon: p.coords.longitude });
          setCargandoGPS(false);
        },
        () => {
          alert("Error: Acceso a GPS denegado.");
          setCargandoGPS(false);
        }
      );
    }
  };

  const handleTransmitir = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ubicacion) return alert("📍 Primero captura las coordenadas GPS.");

    try {
      const response = await fetch('http://127.0.0.1:8000/reportar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: ubicacion.lat,
          lon: ubicacion.lon,
          tipo: tipo,
          severidad: parseInt(severidad),
          notas: notas,
          fecha: new Date().toISOString().split('T')[0]
        })
      });

      if (response.ok) {
        setEnviado(true);
        setTimeout(() => {
          setEnviado(false);
          setUbicacion(null);
          setNotas('');
        }, 3000);
      } else {
        throw new Error();
      }
    } catch {
      alert("❌ Error de comunicación con el servidor Python. ¿Está encendido?");
    }
  };

  return (
    <div className="min-h-screen bg-[#050a07] text-white flex justify-center p-4">
      <div className="w-full max-w-md bg-[#0a150f] border border-[#1a3324] rounded-2xl p-6 flex flex-col shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">🚨</span>
            <h1 className="text-sm font-black uppercase tracking-widest text-emerald-500">URBIPREX</h1>
          </div>
          <button onClick={onBackToDashboard} className="text-[10px] text-gray-500 underline">Cerrar</button>
        </div>

        {enviado ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-pulse">
            <div className="text-5xl mb-4">✅</div>
            <h2 className="text-lg font-bold text-emerald-400">TRANSMISIÓN EXITOSA</h2>
            <p className="text-xs text-gray-500">Datos integrados a la red táctica.</p>
          </div>
        ) : (
          <form onSubmit={handleTransmitir} className="space-y-6">
            <button type="button" onClick={capturarGPS} className="w-full py-5 bg-[#11241a] border border-[#1f402d] rounded-xl flex flex-col items-center hover:border-emerald-500/50 transition-colors">
              <span className="text-2xl mb-1">{ubicacion ? '📍' : '📡'}</span>
              <span className="text-[10px] font-bold uppercase">{cargandoGPS ? 'Localizando...' : 'EXTRAER UBICACIÓN GPS'}</span>
              {ubicacion && <span className="text-[9px] font-mono mt-1 text-emerald-400">{ubicacion.lat.toFixed(5)}, {ubicacion.lon.toFixed(5)}</span>}
            </button>

            <div>
              <label className="text-[9px] uppercase font-bold text-gray-500 mb-2 block tracking-widest">Tipo de Siniestro</label>
              <select value={tipo} onChange={e => setTipo(e.target.value)} className="w-full bg-[#11241a] border border-[#1f402d] rounded-lg p-3 text-sm focus:outline-none focus:border-emerald-500">
                <option value="falla_electrica">⚡ Falla Eléctrica</option>
                <option value="incendio_estructural">🔥 Incendio Estructural</option>
                <option value="fuga_gas">💨 Fuga de Gas</option>
                <option value="maleza">🌿 Incendio en Maleza</option>
              </select>
            </div>

            <div>
              <label className="text-[9px] uppercase font-bold text-gray-500 mb-2 block tracking-widest flex justify-between">
                <span>Severidad</span>
                <span className="text-emerald-400">Nivel {severidad}</span>
              </label>
              <input type="range" min="1" max="3" value={severidad} onChange={e => setSeveridad(e.target.value)} className="w-full h-2 accent-emerald-500 bg-gray-800 rounded-lg appearance-none cursor-pointer" />
            </div>

            <div>
              <label className="text-[9px] uppercase font-bold text-gray-500 mb-2 block tracking-widest">OBSERVACIONES DE CAMPO</label>
              <textarea value={notas} onChange={e => setNotas(e.target.value)} placeholder="Breve descripción..." className="w-full bg-[#11241a] border border-[#1f402d] rounded-lg p-3 text-sm h-24 resize-none focus:outline-none focus:border-emerald-500" />
            </div>

            <button type="submit" className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-black uppercase tracking-widest shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all active:scale-95">
              AGREGAR INCIDENTE A URBIPREX
            </button>
          </form>
        )}
      </div>
    </div>
  );
}