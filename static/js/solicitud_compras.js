// =====================================================
// CIAN CCR — Script para "Iniciativas de Compra"
// =====================================================

// Filtro rápido (simulación)
document.getElementById('btnFiltrar').addEventListener('click', () => {
  const estado = document.getElementById('filtroEstado').value;
  const responsable = document.getElementById('filtroResponsable').value;
  alert(`Filtrando por estado: ${estado || 'Todos'} y responsable: ${responsable || 'Todos'}`);
});

// Limpiar filtros
document.getElementById('btnLimpiar').addEventListener('click', () => {
  document.getElementById('filtroEstado').value = '';
  document.getElementById('filtroResponsable').value = '';
  document.getElementById('filtroInicio').value = '';
});

// Nueva iniciativa
document.getElementById('btnNuevaIniciativa').addEventListener('click', () => {
  alert('Formulario para registrar una nueva iniciativa próximamente disponible.');
});
