import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export const generarReporteTactico = (
  manzana: any,
  weather: any,
  simulador: any
) => {
  if (!manzana) {
    alert("Por favor selecciona una zona en el mapa antes de exportar.");
    return;
  }

  const doc = new jsPDF('p', 'mm', 'letter');
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  // ==========================================
  // DATOS REALES (CERO SIMULACIONES)
  // ==========================================
  const prop = manzana;
  const cvegeo = prop.CVEGEO ? String(prop.CVEGEO) : '';
  
  let nombreZona = 'Sector Desconocido';
  const nombreColonia = prop.colonia || prop.NOM_COL || '';
  if (nombreColonia && nombreColonia.toLowerCase() !== 'colonia no especificada') {
    nombreZona = nombreColonia;
  } else if (cvegeo.length === 16) {
    nombreZona = `Sector ${cvegeo.substring(9, 13)} / Mza ${cvegeo.substring(13, 16)}`;
  }

  const probabilidadIA = (prop.ia_probabilidad_incendio || 0) * 100;
  
  // Lógica del Semáforo de Riesgos (Insignias)
  let nivelRiesgo = "BAJO";
  let colorRiesgo: [number, number, number] = [46, 125, 50]; // Verde (#2e7d32)
  let textoRiesgo: [number, number, number] = [255, 255, 255]; // Blanco
  
  if (probabilidadIA > 65) {
    nivelRiesgo = "CRÍTICO";
    colorRiesgo = [0, 0, 0]; // Negro (#000000)
  } else if (probabilidadIA > 40) {
    nivelRiesgo = "ALTO";
    colorRiesgo = [198, 40, 40]; // Rojo (#c62828)
  } else if (probabilidadIA > 20) {
    nivelRiesgo = "MEDIO";
    colorRiesgo = [249, 168, 37]; // Amarillo/Naranja (#f9a825)
    textoRiesgo = [0, 0, 0]; // Texto negro para que se lea en fondo amarillo
  }

  // ==========================================
  // ENCABEZADO INSTITUCIONAL (Estilo de tu HTML)
  // ==========================================
  // Línea gruesa azul oscuro
  doc.setDrawColor(0, 46, 99); 
  doc.setLineWidth(1.5);
  doc.line(14, 30, pageWidth - 14, 30);

  doc.setTextColor(0, 46, 99);
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text("Ficha Técnica Predictiva", pageWidth / 2, 20, { align: "center" });
  
  doc.setTextColor(85, 85, 85);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text("Dirección General de Protección Civil - URBIPREX", pageWidth / 2, 26, { align: "center" });

  // Folio dinámico en Rojo
  doc.setTextColor(211, 47, 47);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  const folioText = cvegeo.length === 16 ? cvegeo.substring(9, 16) : '0000000';
  doc.text(`FOLIO: PC-PRD-${folioText}`, pageWidth - 14, 38, { align: "right" });

  // Función para dibujar las "Barras Azules" de tus Section Titles
  const drawSectionTitle = (text: string, y: number) => {
    doc.setFillColor(0, 46, 99);
    doc.rect(14, y, pageWidth - 28, 8, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text(text, 18, y + 5.5);
    return y + 10;
  };

  // ==========================================
  // 1. IDENTIFICACIÓN DE LA ZONA
  // ==========================================
  let startY = drawSectionTitle("1. IDENTIFICACIÓN DE LA ZONA", 42);
  
  autoTable(doc, {
    startY: startY,
    head: [],
    body: [
      ['Sector / Colonia:', nombreZona],
      ['Clave Geoestadística (CVEGEO):', cvegeo || 'N/D'],
      ['Población Expuesta (Censo 2020):', `${prop.poblacion_total ? Math.round(prop.poblacion_total) : 0} habitantes`],
      ['Siniestros Históricos Reales:', `${prop.total_incendios || 0} incidentes registrados`]
    ],
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 6, textColor: [51, 51, 51] },
    columnStyles: { 
        0: { fontStyle: 'bold', fillColor: [244, 244, 244], textColor: [0, 46, 99], cellWidth: 70 },
        1: { cellWidth: 'auto' }
    }
  });

  // ==========================================
  // 2. EVALUACIÓN DE RIESGO PREDICTIVO (IA)
  // ==========================================
  startY = (doc as any).lastAutoTable.finalY + 10;
  startY = drawSectionTitle("2. EVALUACIÓN DE RIESGO PREDICTIVO (IA)", startY);
  
  autoTable(doc, {
    startY: startY,
    head: [],
    body: [
      ['Nivel de Riesgo:', `            ${nivelRiesgo}`], // Espacios para dejarle lugar a la insignia de color
      ['Probabilidad Matemática:', `${probabilidadIA.toFixed(2)}%`],
      ['Aislamiento Táctico:', `${(prop.aislamiento_tactico || 0).toFixed(2)} (Vector)`],
      ['Riesgo Urbano Mixto:', `${(prop.riesgo_pob_vial || 0).toFixed(2)} (Vector)`]
    ],
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 6, textColor: [51, 51, 51] },
    columnStyles: { 
        0: { fontStyle: 'bold', fillColor: [244, 244, 244], textColor: [0, 46, 99], cellWidth: 70 },
        1: { cellWidth: 'auto', fontStyle: 'bold' }
    },
    // Hook avanzado para dibujar la insignia de color "Risk Badge" estilo HTML
    didDrawCell: (data) => {
        if (data.row.index === 0 && data.column.index === 1 && data.cell.section === 'body') {
            const x = data.cell.x + 3;
            const y = data.cell.y + 1.5;
            const w = 28;
            const h = data.cell.height - 3;
            
            // Dibujar rectángulo del badge
            doc.setFillColor(colorRiesgo[0], colorRiesgo[1], colorRiesgo[2]);
            doc.rect(x, y, w, h, 'F');
            
            // Dibujar texto del badge
            doc.setTextColor(textoRiesgo[0], textoRiesgo[1], textoRiesgo[2]);
            doc.setFontSize(8);
            doc.setFont('helvetica', 'bold');
            doc.text(nivelRiesgo, x + w/2, y + h/2 + 1, { align: 'center' });
        }
    }
  });

  // ==========================================
  // 3. DESCRIPCIÓN Y JUSTIFICACIÓN ESPACIAL
  // ==========================================
  startY = (doc as any).lastAutoTable.finalY + 10;
  startY = drawSectionTitle("3. JUSTIFICACIÓN ESPACIAL (FUENTES ABIERTAS)", startY);
  
  autoTable(doc, {
    startY: startY,
    head: [],
    body: [
      ['Distancia a Bomberos:', `${(prop.acceso_bomberos_km || 0).toFixed(2)} km`],
      ['Densidad Poblacional:', `${(prop.densidad_pob || 0).toFixed(2)} hab/ha`],
      ['Densidad Vial:', `${(prop.densidad_vial || 0).toFixed(2)} km/ha`],
      ['Modelo Predictivo Base:', 'Random Forest Classifier (Sklearn)']
    ],
    theme: 'grid',
    styles: { fontSize: 10, cellPadding: 6, textColor: [51, 51, 51] },
    columnStyles: { 
        0: { fontStyle: 'bold', fillColor: [244, 244, 244], textColor: [0, 46, 99], cellWidth: 70 },
        1: { cellWidth: 'auto' }
    }
  });

  // Texto explicativo (como el <div class="narrative"> de tu HTML)
  startY = (doc as any).lastAutoTable.finalY + 10;
  doc.setTextColor(85, 85, 85);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  const nota = "Nota Técnica: El dictamen mostrado es generado automáticamente por el algoritmo de Inteligencia Artificial basado en métricas geoespaciales reales extraídas del Instituto Nacional de Estadística y Geografía (INEGI) y OpenStreetMap.";
  const lineasNota = doc.splitTextToSize(nota, pageWidth - 28);
  doc.text(lineasNota, 14, startY);

  // ==========================================
  // PIE DE PÁGINA
  // ==========================================
  doc.setDrawColor(204, 204, 204);
  doc.setLineWidth(0.5);
  doc.line(14, pageHeight - 20, pageWidth - 14, pageHeight - 20);
  
  doc.setTextColor(119, 119, 119);
  doc.setFontSize(8);
  doc.text("Hoja 1 de Reporte | Generado por URBIPREX para integración en Atlas de Riesgo", pageWidth / 2, pageHeight - 15, { align: "center" });

  // Guardar archivo
  doc.save(`Ficha_PC_Predictiva_${cvegeo || 'General'}.pdf`);
};