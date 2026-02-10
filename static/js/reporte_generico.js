// =========================
// Utilidades y navegación
// =========================

/* ===== Navegación limpia al refrescar ===== */
(function () {
  const nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
  const isReload = nav ? nav.type === 'reload' : (performance.navigation && performance.navigation.type === 1);
  window.addEventListener('pageshow', function (e) { if (e.persisted) window.location.replace(window.location.pathname); });
  if (isReload) window.location.replace(window.location.pathname);
})();

/* Polyfill CSS.escape */
if (typeof CSS === 'undefined' || typeof CSS.escape !== 'function') {
  window.CSS = window.CSS || {}; CSS.escape = s => String(s).replace(/[^a-zA-Z0-9_\-]/g, ch => '\\' + ch);
}

/* ===== Helpers de fechas / límite 5 meses ===== */
const MESES_MAX = 5;
function hoy00(){ const d=new Date(); d.setHours(0,0,0,0); return d; }
function limiteFecha(){ const d=hoy00(); d.setMonth(d.getMonth()-MESES_MAX); d.setHours(0,0,0,0); return d; }
function fmtYMD(d){ return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; }
function setFlatpickrRange(iDesde, iHasta, d1, d2){
  if (iDesde?._flatpickr) iDesde._flatpickr.setDate(d1, true); else iDesde.value = fmtYMD(d1);
  if (iHasta?._flatpickr) iHasta._flatpickr.setDate(d2, true); else iHasta.value = fmtYMD(d2);
}

/* ===== Toast ===== */
function toast(msg, icon = 'success', ms = 6000){
  const Toaster = Swal.mixin({
    toast: true, position: 'top-end', showConfirmButton: false, showCloseButton: true,
    timer: ms, timerProgressBar: true,
    didOpen: (el) => { el.addEventListener('mouseenter', Swal.stopTimer); el.addEventListener('mouseleave', Swal.resumeTimer); }
  });
  Toaster.fire({ icon, title: msg });
}

// --- Modal de carga: cerrar solo el "loading", no los toasts ---
let __loadingOpen = false;
function openLoadingModal(title = 'Generando reporte…') {
  __loadingOpen = true;
  Swal.fire({
    title, allowOutsideClick: false, allowEscapeKey: false,
    didOpen: () => { const popup = Swal.getPopup(); if (popup) popup.dataset.role = 'loading'; Swal.showLoading(); },
    willClose: () => { __loadingOpen = false; }
  });
}
function closeLoadingModal() {
  const popup = Swal.getPopup();
  const isToast = popup?.classList?.contains('swal2-toast');
  const isLoading = popup?.dataset?.role === 'loading';
  if (__loadingOpen && isLoading && !isToast && Swal.isVisible()) Swal.close();
}

/* ===== Validaciones ===== */
function inputsCandidatos(){ return Array.from(document.querySelectorAll('.form-filtro input[name], .form-filtro select[name]')); }
function hayAlMenosUnFiltro(){ return inputsCandidatos().some(i => (i.value||'').trim() !== ''); }
function parseLocalYMD(s){ if (!s) return new Date(NaN); const [y,m,d] = s.split('-').map(Number); return new Date(y,(m||1)-1,d||1,0,0,0,0); }

function validarRangos(){
  const errores = []; const bases = {}; const hoy = hoy00(); const limite = limiteFecha();
  document.querySelectorAll('.form-filtro [data-par]').forEach(inp=>{
    const name = inp.name || '';
    const base = name.startsWith('desde_') ? name.slice(6) : name.startsWith('hasta_') ? name.slice(6) : null;
    if(!base) return;
    bases[base] ??= { tipo: inp.dataset.tipo, desde:'', hasta:'' };
    if (name.startsWith('desde_')) bases[base].desde = (inp.value||'').trim();
    if (name.startsWith('hasta_')) bases[base].hasta = (inp.value||'').trim();
  });

  document.querySelectorAll('.is-invalid').forEach(el=>el.classList.remove('is-invalid'));
  const markInvalid = (nDesde, nHasta) => { nDesde?.classList.add('is-invalid'); nHasta?.classList.add('is-invalid'); };

  for (const [base, b] of Object.entries(bases)){
    const nDesde = document.querySelector(`[name="desde_${CSS.escape(base)}"]`);
    const nHasta = document.querySelector(`[name="hasta_${CSS.escape(base)}"]`);

    if ((b.desde && !b.hasta) || (!b.desde && b.hasta)){
      errores.push(`Completa el rango de ${base}: desde_ y hasta_.`); markInvalid(nDesde, nHasta); continue;
    }
    if (b.desde && b.hasta){
      if (b.tipo === 'date'){
        const d1 = parseLocalYMD(b.desde), d2 = parseLocalYMD(b.hasta);
        if (isNaN(d1) || isNaN(d2)){ errores.push(`Rango de fechas inválido en ${base}.`); markInvalid(nDesde, nHasta); continue; }
        if (d1 > d2){ errores.push(`Rango de fechas inválido en ${base} (desde > hasta).`); markInvalid(nDesde, nHasta); }
        if (d1 < limite){ errores.push(`El rango en ${base} excede el límite: solo desde ${fmtYMD(limite)} en adelante (máx. ${MESES_MAX} meses).`); markInvalid(nDesde, nHasta); }
        if (d2 > hoy){ errores.push(`La fecha 'hasta' en ${base} no puede ser futura (máx. ${fmtYMD(hoy)}).`); markInvalid(nDesde, nHasta); }
      } else {
        const n1 = parseFloat(b.desde), n2 = parseFloat(b.hasta);
        if (!isNaN(n1) && !isNaN(n2) && n1 > n2){ errores.push(`Rango numérico inválido en ${base} (desde > hasta).`); markInvalid(nDesde, nHasta); }
      }
    }
  }
  return errores;
}

function asegurarRangos() {
  document.querySelectorAll('.rango-fecha').forEach(sel=>{
    const base  = sel.dataset.base; const code  = sel.value || '7d';
    const iDesde = document.querySelector(`[name="desde_${CSS.escape(base)}"]`);
    const iHasta = document.querySelector(`[name="hasta_${CSS.escape(base)}"]`);
    if (!iDesde || !iHasta) return;
    const faltaValor = !(iDesde.value && iHasta.value);
    if (code !== 'custom' && faltaValor) {
      const {desde, hasta} = calcularRango(code);
      if (desde && hasta) setFlatpickrRange(iDesde, iHasta, desde, hasta);
    }
  });
}

let enviando = false;
function validarCampos () {
  if (enviando) return false;
  if (Swal.isVisible()) Swal.close();
  asegurarRangos();

  const errores = [];
  if (!hayAlMenosUnFiltro()){
    errores.push('Debes completar al menos <b>un filtro</b> para generar el reporte.');
    document.getElementById('avisoMinimo').classList.remove('d-none');
  } else {
    document.getElementById('avisoMinimo').classList.add('d-none');
  }
  errores.push(...validarRangos());

  if (errores.length) {
    const html = '<ul style="text-align:left;margin:0;padding-left:1rem">' + errores.map(e=>`<li>${e}</li>`).join('') + '</ul>';
    Swal.fire({ icon:'warning', title:'Revisa los filtros', html, confirmButtonText:'Entendido' });
    return false;
  }

  openLoadingModal('Generando reporte…');
  enviando = true; // se libera en draw/error
  return true;
}

/* ===== Presets de rango ===== */
function startOfMonth(d){ const x=new Date(d); x.setDate(1); x.setHours(0,0,0,0); return x; }
function endOfPrevMonth(d){ const x=new Date(d); x.setDate(0); x.setHours(0,0,0,0); return x; }

function calcularRango(code){
  const today = hoy00(); const limite = limiteFecha(); let desde=null, hasta=null;
  if (code === '7d') { desde = new Date(today.getFullYear(), today.getMonth(), today.getDate()-6); hasta = today; }
  else if (code === 'lm') { desde = startOfMonth(new Date(today.getFullYear(), today.getMonth()-1, 1)); hasta = endOfPrevMonth(new Date(today.getFullYear(), today.getMonth(), 1)); }
  else if (code === '5m') { desde = new Date(today.getFullYear(), today.getMonth()-5, today.getDate()); hasta = today; }
  else if (code === 'tm') { desde = startOfMonth(today); hasta = hoy00(); }
  else { return {}; }
  if (desde < limite) desde = limite; if (hasta > today) hasta = today; return {desde, hasta};
}
function toggleCustom(base, show){
  const box = document.querySelector(`[name="desde_${CSS.escape(base)}"]`)?.closest('.custom-box');
  const wrap = box?.closest('.range-inline'); if (wrap) wrap.dataset.mode = show ? 'custom' : 'preset';
}
function aplicarRango(base, code){
  const iDesde = document.querySelector(`[name="desde_${CSS.escape(base)}"]`);
  const iHasta = document.querySelector(`[name="hasta_${CSS.escape(base)}"]`);
  if(!iDesde || !iHasta) return;
  if (code === 'custom'){ toggleCustom(base, true); iDesde._flatpickr?.redraw(); iHasta._flatpickr?.redraw(); return; }
  toggleCustom(base, false);
  const {desde, hasta} = calcularRango(code); if(!desde || !hasta) return;
  setFlatpickrRange(iDesde, iHasta, desde, hasta);
}

/* ===== Limpiar (corregido) ===== */

function limpiarTabla(){
  const tabla = document.getElementById('tablaResultados');
  if (!tabla) return;
  const tbody = tabla.querySelector('tbody');
  if (tbody) tbody.innerHTML = '';
}

// Abortar XHR de DataTables en curso (evita reinyecciones tardías)
function abortDT($tabla){
  try {
    if (!$.fn.dataTable || !$.fn.dataTable.isDataTable($tabla[0])) return;
    const api = $tabla.DataTable();
    const settings = api.settings()[0];
    const jq = settings && settings.jqXHR;
    if (jq && jq.readyState !== 4) { try { jq.abort(); } catch {} }
  } catch {}
}

// Destruir DataTables y “desenvolver” los contenedores
function destroyDT($tabla){
  try {
    if ($.fn.dataTable && $.fn.dataTable.isDataTable($tabla[0])) {
      $(window).off('.dtfix .dtclose');
      $tabla.off('.dtfix .dtclose');
      $('#tablaContenedor .dataTables_scrollBody').off('.dtfix .dtclose');
      $tabla.DataTable().clear().destroy(true);
    }
  } catch (e) { console.warn('DT destroy warn:', e); }

  // Quitar wrappers residuales con seguridad
  (function unwrapDT(){
    const cont = document.getElementById('tablaContenedor');
    if (!cont) return;

    const wrap = cont.querySelector('.dataTables_wrapper');
    if (wrap) {
      const table = wrap.querySelector('#tablaResultados');
      if (table) { wrap.parentNode.insertBefore(table, wrap); }
      wrap.remove();
    }
    const scrollWrap = cont.querySelector('.dataTables_scroll');
    if (scrollWrap) {
      const table2 = scrollWrap.querySelector('#tablaResultados');
      if (table2) { scrollWrap.parentNode.insertBefore(table2, scrollWrap); }
      scrollWrap.remove();
    }
    cont.classList.remove('dt-hide-until-ready');
    cont.querySelectorAll('.dataTables_processing').forEach(n => n.remove());
  })();
}

function limpiarFiltros(){
  try { if (Swal.isVisible()) Swal.close(); } catch {}
  try { closeLoadingModal?.(); } catch {}
  window.enviando = false;

  const $tabla = $('#tablaResultados');
  abortDT($tabla);
  destroyDT($tabla);

  // 1) Resetear inputs/selects/textarea y flatpickr
  document.querySelectorAll('.form-filtro input, .form-filtro select, .form-filtro textarea')
    .forEach(el => {
      el.classList.remove('is-invalid');
      if (el.type === 'checkbox' || el.type === 'radio') el.checked = false;
      else el.value = '';
      if (el._flatpickr) el._flatpickr.clear();
    });

  // 2) Restablecer presets de rango y ocultar el bloque custom
  document.querySelectorAll('.rango-fecha').forEach(sel => {
    const base = sel.dataset.base;
    sel.value = '7d';
    aplicarRango(base, '7d');
    toggleCustom(base, false);
  });

  // 3) Avisos / botones
  document.getElementById('avisoMinimo')?.classList.add('d-none');
  document.getElementById('btnExportar')?.setAttribute('disabled', 'true');
  document.getElementById('btnLimpiar')?.setAttribute('disabled', 'true');

  // 4) Vaciar tbody de la tabla base
  limpiarTabla();

  // 5) Señal para re-init al próximo "Generar"
  window.__forceInitDT = true;
}

/* ===== Init filtros / flatpickr / botones ===== */
document.addEventListener("DOMContentLoaded", function () {
  if (typeof flatpickr === 'function') {
    flatpickr(".flatpickr", {
      dateFormat: "Y-m-d", allowInput: true,
      locale: (window.flatpickr?.l10ns?.es) || "es",
      minDate: fmtYMD(limiteFecha()), maxDate: fmtYMD(hoy00())
    });
  }
  document.querySelectorAll('.rango-fecha').forEach(sel=>{
    const base = sel.dataset.base;
    const iDesde = document.querySelector(`[name="desde_${CSS.escape(base)}"]`);
    const iHasta = document.querySelector(`[name="hasta_${CSS.escape(base)}"]`);
    const yaTiene = (iDesde && iDesde.value) || (iHasta && iHasta.value);
    if (yaTiene){ sel.value='custom'; toggleCustom(base, true); }
    else { if (!sel.value) sel.value='7d'; aplicarRango(base, sel.value); toggleCustom(base, sel.value==='custom'); }
    sel.addEventListener('change', ()=>{ aplicarRango(base, sel.value); toggleCustom(base, sel.value === 'custom'); });
  });

  const tieneResultados = !!document.querySelector('#tablaResultados tbody tr');
  const btnExp = document.getElementById('btnExportar');
  const btnLim = document.getElementById('btnLimpiar');
  if (btnExp) btnExp.disabled = !tieneResultados;
  if (btnLim) btnLim.disabled = !tieneResultados && !hayAlMenosUnFiltro();

  document.querySelectorAll('.form-filtro input, .form-filtro select').forEach(i=>{
    i.addEventListener('input', ()=>{ document.getElementById('avisoMinimo').classList.add('d-none'); i.classList.remove('is-invalid'); });
  });

  // Enter para generar
  document.getElementById('formFiltros')?.addEventListener('keydown', e=>{
    if(e.key==='Enter'){ e.preventDefault(); document.getElementById('btnGenerar')?.click(); }
  });

  // >>> Cambiado: Click "Limpiar" = recarga limpia (como F5) <<<
  btnLim?.addEventListener('click', (e) => {
  e.preventDefault();
  try { if (Swal.isVisible()) Swal.close(); } catch {}
  // Muestra modal de carga a pantalla completa
  openLoadingModal('Limpiando…');

  // Da 1 frame para pintar el spinner y luego recarga limpia la ruta
  requestAnimationFrame(() => {
    setTimeout(() => {
      location.replace(location.pathname); // recarga sin historial ni query
    }, 60);
  });
});

/* ===== DataTables: init robusto, con server-side y render estable ===== */
$(function () {
  const $tabla = $('#tablaResultados');
  const $wrap  = $('#tablaContenedor');
  if (!$tabla.length || !$.fn.DataTable) return;

  // Si ya existe, destruye y limpia listeners (evita doble init y callbacks sobre DOM destruido)
  if ($.fn.dataTable.isDataTable($tabla[0])) {
    $(window).off('.dtfix .dtclose');
    $tabla.off('.dtfix .dtclose');
    $('#tablaContenedor .dataTables_scrollBody').off('.dtfix .dtclose');
    $tabla.DataTable().clear().destroy(true);
  }

  // Oculta mientras inicializa para evitar parpadeo
  $wrap.addClass('dt-hide-until-ready');

  // === Helper: espera a que el DOM quede “quieto” y fallback duro ===
  function waitForStableRender(opts = {}) {
    const minQuietMs = opts.minQuietMs ?? 200;
    const timeoutMs  = opts.timeoutMs  ?? 12000;
    const wrap = document.querySelector('#tablaContenedor');
    const body = wrap?.querySelector('.dataTables_scrollBody');
    const head = wrap?.querySelector('.dataTables_scrollHead');
    if (!wrap || !body) return Promise.resolve();

    return new Promise(resolve => {
      let lastChange = performance.now();
      const mark = () => { lastChange = performance.now(); };

      const mo = new MutationObserver(mark);
      mo.observe(body, { childList:true, subtree:true, attributes:true });

      const ro = new ResizeObserver(mark);
      ro.observe(body); if (head) ro.observe(head); ro.observe(wrap);

      const start = performance.now();
      (function loop(){
        const now = performance.now();
        const quietFor = now - lastChange;
        const timedOut = (now - start) > timeoutMs;
        if (quietFor >= minQuietMs || timedOut) {
          try { mo.disconnect(); } catch {}
          try { ro.disconnect(); } catch {}
          requestAnimationFrame(async () => {
            try { if (document.fonts?.ready) await document.fonts.ready; } catch {}
            requestAnimationFrame(resolve);
          });
        } else {
          requestAnimationFrame(loop);
        }
      })();
    });
  }

  // === Programar cierre del loader EN CADA draw de recarga (+fallback) ===
  function scheduleCloseOnNextDraw($t, $w){
    const settleAndShow = () => {
      const hardTimeout = setTimeout(() => {
        $w.removeClass('dt-hide-until-ready');
        closeLoadingModal();
        enviando = false;
        try { $t.DataTable().columns.adjust(); } catch {}
      }, 8000);

      waitForStableRender({ minQuietMs: 200, timeoutMs: 12000 }).then(() => {
        clearTimeout(hardTimeout);
        $w.removeClass('dt-hide-until-ready');
        closeLoadingModal();
        enviando = false;
        try { $t.DataTable().columns.adjust(); } catch {}
      });
    };
    $t.off('draw.dt.dtclose');
    $t.one('draw.dt.dtclose', settleAndShow);
  }

  // === Filtros del formulario → object plano (solo con valor) ===
  function getFiltros() {
    const out = {};
    document.querySelectorAll('.form-filtro [name]').forEach(i=>{
      const v = (i.value || '').trim();
      if (v) out[i.name] = v;
    });
    return out;
  }

  // Exponer init global (lo llamas desde tu flujo al generar)
  window.initDT = function initDT() {
    if ($.fn.dataTable.isDataTable($tabla[0])) {
      $(window).off('.dtfix .dtclose');
      $tabla.off('.dtfix .dtclose');
      $('#tablaContenedor .dataTables_scrollBody').off('.dtfix .dtclose');
      $tabla.DataTable().clear().destroy(true);
    }

    $wrap.addClass('dt-hide-until-ready');

    const dt = $tabla.DataTable({
      serverSide: true,
      processing: true,
      deferRender: true,
      searchDelay: 400,
      autoWidth: false,
      fixedHeader: false,

      scrollX: true,
      scrollY: '52vh',
      scrollCollapse: true,

      paging: true,
      pageLength: 25,
      lengthMenu: [[25,50,100,200],[25,50,100,200]],

      // 🔻 sin "f" para que no aparezca el input
      dom: '<"dt-toolbar d-flex flex-wrap align-items-center justify-content-between mb-2"l>t<"dt-footer d-flex flex-wrap align-items-center justify-content-between mt-2"ip>',
      searching: false, // 🔻 desactivar búsqueda global
      language: { url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json' },

      ajax: {
        url: `/api/reporte_data/${encodeURIComponent(window.REPORTE_RUTA || '')}`,
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': window.CSRF_TOKEN || '' },
        data: (d) => JSON.stringify({ ...d, filtros: getFiltros() }),
        error: function(){
          $('#tablaContenedor').removeClass('dt-hide-until-ready');
          closeLoadingModal();
          enviando = false;
          toast('Ocurrió un error al cargar el reporte.', 'error');
        }
      },

      initComplete: function () {
        const api = this.api();

        const fix = () => {
          try {
            if (!api || !api.settings()[0] || !api.table || !$tabla.length || !$.fn.dataTable.isDataTable($tabla[0])) return;
            api.columns.adjust();
          } catch {}
        };

        const syncHeadPadding = () => {
          const wrap = document.querySelector('#tablaContenedor');
          if (!wrap || !$tabla.length || !$.fn.dataTable.isDataTable($tabla[0])) return;
          const head = wrap.querySelector('.dataTables_scrollHead');
          const body = wrap.querySelector('.dataTables_scrollBody');
          if (!head || !body) return;
          const sbw = Math.max(0, body.offsetWidth - body.clientWidth);
          const val = sbw ? `${sbw}px` : '0px';
          try {
            head.style.setProperty('--dt-sbw', val);
            wrap.style.setProperty('--dt-sbw', val);
          } catch {}
        };

        syncHeadPadding();
        setTimeout(syncHeadPadding, 40);
        setTimeout(syncHeadPadding, 140);

        $(window).on('resize.dtfix', () => { syncHeadPadding(); fix(); });
        const bodyNode = document.querySelector('#tablaContenedor .dataTables_scrollBody');
        if (bodyNode) {
          bodyNode.addEventListener('scroll',     syncHeadPadding, { passive: true });
          bodyNode.addEventListener('mouseenter', syncHeadPadding, { passive: true });
          bodyNode.addEventListener('mouseleave', syncHeadPadding, { passive: true });
        }

        $('#tablaResultados_filter input').attr({ placeholder: 'Buscar en la tabla…', 'aria-label': 'Buscar en la tabla' });

        fix(); requestAnimationFrame(fix); setTimeout(fix, 120); setTimeout(fix, 300);

        $('[data-bs-toggle="tab"],[data-bs-toggle="collapse"]').on('shown.bs.tab shown.bs.collapse.dtfix', () => { syncHeadPadding(); fix(); });

        $tabla.on('destroy.dtfix', () => {
          $(window).off('.dtfix .dtclose');
          $tabla.off('.dtfix .dtclose');
          $('#tablaContenedor .dataTables_scrollBody').off('.dtfix .dtclose');
        });
      },

      drawCallback: function () {
        try {
          if ($tabla.length && $.fn.dataTable.isDataTable($tabla[0])) {
            this.api().columns.adjust();
          }
        } catch {}
      }
    });

    // Cerrar loader en el PRIMER draw tras init
    scheduleCloseOnNextDraw($tabla, $wrap);

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        try { if ($tabla.length && $.fn.dataTable.isDataTable($tabla[0])) dt.columns.adjust(); } catch {}
      });
    }

    $tabla.on('error.dt.resetFlag', () => { enviando = false; });
  };

  // === Toggle de botones según resultados ===
  function toggleBotonesPorDatos(api, json){
    const hasData = json
      ? ((json.recordsDisplay ?? json.recordsTotal ?? 0) > 0)
      : (api.rows({ filter: 'applied' }).count() > 0);
    $('#btnExportar').prop('disabled', !hasData);
    $('#btnLimpiar').prop('disabled', !(hayAlMenosUnFiltro() || hasData));
  }

  // Cuando llega la respuesta del servidor (más confiable para serverSide)
  $tabla.on('xhr.dt', function (e, settings, json) {
    const api = $tabla.DataTable();
    toggleBotonesPorDatos(api, json);
    // Mostrar el wrapper en cuanto responde el server
    $('#tablaContenedor').removeClass('dt-hide-until-ready');
  });

  // Fallback por si algo cambia en draw (ej. búsquedas locales, etc.)
  $tabla.on('draw.dt', function () {
    const api = $tabla.DataTable();
    toggleBotonesPorDatos(api, null);
  });

  // Inicia tras las fuentes si es posible (mejor alineación desde el 1er render)
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => window.initDT());
  } else {
    window.initDT();
  }

  // Botón "Generar": recarga con filtros actuales y programa cierre del loader
  const btnGen = document.getElementById('btnGenerar');
  if (btnGen) {
    btnGen.addEventListener('click', () => {
      const ok = typeof validarCampos === 'function' ? validarCampos() : true;
      if (!ok) return;

      // Por si acaso, aseguramos mostrar el wrapper antes de recargar/inicializar
      $('#tablaContenedor').removeClass('dt-hide-until-ready');

      if (window.__forceInitDT) {
        window.__forceInitDT = false;
        window.initDT();            // re-inicializa tras "Limpiar"
        return;
      }

      if ($.fn.dataTable.isDataTable($tabla[0])) {
        // programar cierre del loader al próximo draw
        (function scheduleCloseOnNextDraw($t, $w){
          const settleAndShow = () => {
            const hardTimeout = setTimeout(() => {
              $w.removeClass('dt-hide-until-ready');
              closeLoadingModal();
              enviando = false;
              try { $t.DataTable().columns.adjust(); } catch {}
            }, 8000);

            (function waitForStableRender(opts = {}) {
              const minQuietMs = opts.minQuietMs ?? 200;
              const timeoutMs  = opts.timeoutMs  ?? 12000;
              const wrap = document.querySelector('#tablaContenedor');
              const body = wrap?.querySelector('.dataTables_scrollBody');
              const head = wrap?.querySelector('.dataTables_scrollHead');
              if (!wrap || !body) return Promise.resolve();
              return new Promise(resolve => {
                let lastChange = performance.now();
                const mark = () => { lastChange = performance.now(); };
                const mo = new MutationObserver(mark);
                mo.observe(body, { childList:true, subtree:true, attributes:true });
                const ro = new ResizeObserver(mark);
                ro.observe(body); if (head) ro.observe(head); ro.observe(wrap);
                const start = performance.now();
                (function loop(){
                  const now = performance.now();
                  const quietFor = now - lastChange;
                  const timedOut = (now - start) > timeoutMs;
                  if (quietFor >= minQuietMs || timedOut) {
                    try { mo.disconnect(); } catch {}
                    try { ro.disconnect(); } catch {}
                    requestAnimationFrame(async () => {
                      try { if (document.fonts?.ready) await document.fonts.ready; } catch {}
                      requestAnimationFrame(resolve);
                    });
                  } else {
                    requestAnimationFrame(loop);
                  }
                })();
              });
            })().then(() => {
              clearTimeout(hardTimeout);
              $w.removeClass('dt-hide-until-ready');
              closeLoadingModal();
              enviando = false;
              try { $t.DataTable().columns.adjust(); } catch {}
            });
          };
          $t.off('draw.dt.dtclose');
          $t.one('draw.dt.dtclose', settleAndShow);
        })($tabla, $wrap);

        $tabla.DataTable().ajax.reload(null, true);
      } else {
        window.initDT();
      }
    });
  }

  // Asegurar que si ocurre un error global de DataTables, se cierre el loader y se muestre el wrapper
  $tabla.on('error.dt', function(){
    $('#tablaContenedor').removeClass('dt-hide-until-ready');
    closeLoadingModal();
    enviando = false;
  });
});
