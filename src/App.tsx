import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Dashboard from './Dashboard';
import AdminCapture from './components/AdminCapture';

// Envoltorio para la app de captura
function CapturaMobile() {
  const navigate = useNavigate();
  return <AdminCapture onBackToDashboard={() => navigate('/')} />;
}

function App() {
  return (
    // 🚦 AQUÍ ESTÁ EL BLINDAJE: Le decimos al enrutador su nombre base
    <Router basename="/URBIPREX">
      <Routes>
        {/* Ruta Principal: El Centro de Mando Táctico */}
        <Route path="/" element={<Dashboard />} />
        
        {/* Ruta Secreta: La App Móvil para los Inspectores en calle */}
        <Route path="/admin" element={<CapturaMobile />} />
      </Routes>
    </Router>
  );
}

export default App;