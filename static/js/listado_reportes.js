/* ==================== fetch helper ==================== */
async function fetchJSON(url, opts) {
  const r = await fetch(url, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok || data?.ok === false) {
    const msg = data?.mensaje || data?.error || ('HTTP ' + r.status);
    throw new Error(msg);
  }
  return data;
}

/* ==================== Eliminar (SweetAlert) ==================== */
function confirmarEliminacion(ruta) {
  Swal.fire({
    title: '¿Eliminar reporte?',
    text: 'Esta acción no se puede deshacer.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  }).then(result => {
    if (!result.isConfirmed) return;

    // Asegura un formulario POST (oculto)
    let form = document.getElementById('formEliminar');
    if (!form) {
      form = document.createElement('form');
      form.id = 'formEliminar';
      form.method = 'POST';
      form.style.display = 'none';
      document.body.appendChild(form);
    }

    form.action = `/eliminar_reporte/${encodeURIComponent(ruta)}`;
    form.submit(); // => POST
  });
}

/* ==================== Buscador en cliente ==================== */
function configurarBuscador() {
  const buscador = document.getElementById("buscadorReportes");
  if (!buscador) return;

  buscador.addEventListener("input", () => {
    const filtro = buscador.value.trim().toLowerCase();
    const tarjetas = document.querySelectorAll(".reporte-card"); // <- filtramos por esta clase

    let visibles = 0;
    tarjetas.forEach(card => {
      const nombre   = (card.getAttribute("data-nombre")   || "").toLowerCase();
      const gerencia = (card.getAttribute("data-gerencia") || "").toLowerCase();
      const visible = nombre.includes(filtro) || gerencia.includes(filtro);
      card.style.display = visible ? "block" : "none";
      if (visible) visibles++;
    });

    // Feedback opcional si no hay resultados
    const noRes = document.getElementById("Resultados");
    if (noRes) noRes.style.display = visibles ? "none" : "block";
  });
}

/* ==================== Toasts por query param (?msg=) ==================== */
function mostrarSwalMensaje() {
  const mensajes = {
    'eliminado': { icon: 'success', text: '✅ Reporte eliminado correctamente.' },
    'creado':   { icon: 'success', text: '🎉 Reporte creado con éxito.' },
    'editado':  { icon: 'info',    text: '✏️ Reporte actualizado.' }
  };

  const msg = new URLSearchParams(window.location.search).get('msg');
  if (!msg || !mensajes[msg]) return;

  Swal.fire({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 2500,
    timerProgressBar: true,
    icon: mensajes[msg].icon,
    title: mensajes[msg].text
  });

  // Limpia el parámetro de la URL
  window.history.replaceState({}, document.title, window.location.pathname);
}

/* ==================== “Reportes varios / compartidos” ==================== */

/**
 * Construye una tarjeta de reporte compatible con:
 *  - Buscador: usa .reporte-card y data-nombre / data-gerencia
 *  - Paginador: el wrapper usa .reporte-item
 */
function buildReporteCard(reporte) {
  const col = document.createElement('div');
  col.className = 'reporte-item col-md-4';

  const nombre   = reporte.nombre || '';
  const desc     = reporte.descripcion || '';
  const gerencia = reporte.gerencia || '';
  const ruta     = (reporte.ruta || '').trim();
  const url      = (reporte.url && reporte.url.trim()) || (ruta ? `/reporte/${encodeURIComponent(ruta)}` : '#');

  col.innerHTML = `
    <div class="card card-reporte reporte-card h-100 shadow-sm border-0 rounded-4 position-relative"
         data-nombre="${nombre.replace(/"/g,'&quot;')}"
         data-gerencia="${gerencia.replace(/"/g,'&quot;')}">
      <div class="card-body d-flex flex-column justify-content-between">
        <div>
          <h5 class="card-title text-truncate mb-1" title="${nombre}">${nombre}</h5>
          <p class="card-subtitle small text-muted text-truncate mb-3" title="${desc}">${desc}</p>
        </div>
        <hr class="card-divider my-2">
        <div class="d-flex justify-content-end gap-2 mt-2 acciones">
          <a href="${url}" class="btn btn-sm btn-light rounded-circle px-2" title="Ver Reporte" data-no-stretch>
            <i class="fas fa-eye text-primary"></i>
          </a>
        </div>
      </div>
      <a class="stretched-link" href="${url}"></a>
    </div>`;
  return col;
}

/**
 * Inserta una sección en el acordeón con contenedor .reportes-container (para el pager)
 */
function appendAccordionSection(container, title, cards) {
  const idx = container.querySelectorAll('.accordion-item').length + 1;
  const item = document.createElement('div');
  item.className = 'accordion-item border-0 shadow-sm mb-2';
  item.innerHTML = `
    <h2 class="accordion-header" id="heading-extra-${idx}">
      <button class="accordion-button collapsed" type="button"
              data-bs-toggle="collapse" data-bs-target="#collapse-extra-${idx}"
              aria-expanded="false" aria-controls="collapse-extra-${idx}">
        <strong><i class="fas fa-folder-open me-2"></i><span class="grupo-nombre">${title}</strong></span>
      </button>
    </h2>
    <div id="collapse-extra-${idx}" class="accordion-collapse collapse"
         aria-labelledby="heading-extra-${idx}" data-bs-parent="#accordionReportes">
      <div class="accordion accordion-custom">
        <div class="reportes-container row g-4"></div>
      </div>
    </div>`;
  const row = item.querySelector('.reportes-container.row.g-4');
  cards.forEach(c => row.appendChild(c));
  container.appendChild(item);
}

async function cargarReportesVarios() {
  try {
    const data = await fetchJSON('/rol/api/mis_reportes');
    const varios = Array.isArray(data?.varios) ? data.varios : [];
    if (!varios.length) return;

    const container = document.getElementById('accordionReportes');
    if (!container) return;

    const cards = varios.map(buildReporteCard);
    appendAccordionSection(container, 'REPORTES COMPARTIDOS', cards);
  } catch (e) {
    console.warn('No se pudieron cargar los “Reportes varios”:', e.message);
  }
}

/* ==================== Paginación client-side ==================== */
// Si usas <nav class="pager"> ... en cada sección, esto lo activa
document.addEventListener('DOMContentLoaded', () => {
  const DEFAULT_PAGE_SIZE = 6;

  // Para cada paginador independiente
  document.querySelectorAll('nav.pager').forEach((pager) => {
    // El contenedor de items es el bloque de reportes justo antes del <nav>
    // Ajusta este selector si tu DOM es diferente
    let container = pager.previousElementSibling;
    if (!container || !container.classList.contains('reportes-container')) {
      // fallback: busca hacia arriba y luego dentro
      container = pager.closest('.accordion-collapse, .accordion-item, body')
                      .querySelector('.reportes-container');
    }
    if (!container) return;

    const items = Array.from(container.querySelectorAll('.reporte-item'));
    const sel = pager.querySelector('.perPageSel');
    const btnPrev = pager.querySelector('.btnPrev');
    const btnNext = pager.querySelector('.btnNext');
    const pageInfo = pager.querySelector('.pageInfo');

    let current = 1;
    const pageSize = () => parseInt(sel?.value || DEFAULT_PAGE_SIZE, 10);
    const totalPages = () => Math.max(1, Math.ceil(items.length / pageSize()));

    function render() {
      const start = (current - 1) * pageSize();
      const end = start + pageSize();

      items.forEach((el, i) => {
        el.style.display = (i >= start && i < end) ? '' : 'none';
      });

      if (pageInfo) pageInfo.textContent = `Página ${current} de ${totalPages()}`;
      if (btnPrev) btnPrev.disabled = current <= 1;
      if (btnNext) btnNext.disabled = current >= totalPages();
    }

    // Eventos
    sel?.addEventListener('change', () => { current = 1; render(); });
    btnPrev?.addEventListener('click', () => { if (current > 1) { current--; render(); }});
    btnNext?.addEventListener('click', () => { if (current < totalPages()) { current++; render(); }});

    // Inicializa
    render();
  });
});

/* ==================== Boot ==================== */
document.addEventListener("DOMContentLoaded", () => {
  configurarBuscador();
  mostrarSwalMensaje();
  cargarReportesVarios();
}); 