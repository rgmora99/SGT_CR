/* ========================== CONFIGURACIÓN DE TEMA ========================== */
/** Cambia a true si quieres permitir modo oscuro en la interfaz */
const ALLOW_DARK = false;
/** Clave de almacenamiento para el tema */
const THEME_STORAGE_KEY = 'theme';

/* ====== Defensa temprana: si NO permitimos dark, fuerza light y limpia ===== */
(() => {
  try {
    if (!ALLOW_DARK) {
      localStorage.removeItem(THEME_STORAGE_KEY);
      if (document.body) document.body.classList.remove('dark');
      document.addEventListener('DOMContentLoaded', () => {
        document.body.classList.remove('dark');
      });
    }
  } catch (_) { /* no-op */ }
})();

/* ================= SweetAlert helpers ================= */
window.swalInfo = (title, msg) =>
  Swal.fire({ icon: 'info', title: title || 'Información', text: msg || '', confirmButtonText: 'OK' });

window.swalOk = (title, msg) =>
  Swal.fire({ icon: 'success', title: title || 'Éxito', text: msg || '', timer: 1800, showConfirmButton: false });

window.swalWarn = (title, msg) =>
  Swal.fire({ icon: 'warning', title: title || 'Atención', text: msg || '', confirmButtonText: 'OK' });

window.swalErr = (title, msg) =>
  Swal.fire({ icon: 'error', title: title || 'Error', text: msg || 'Ocurrió un error.' });

window.swalAsk = (title, msg) =>
  Swal.fire({
    icon: 'question',
    title: title || '¿Confirmar?',
    text: msg || '',
    showCancelButton: true,
    confirmButtonText: 'Sí',
    cancelButtonText: 'No'
  });

window.swalPrompt = async (title, msg, def = '') => {
  const { value } = await Swal.fire({
    title: title || 'Ingrese un valor',
    input: 'text',
    inputLabel: msg || '',
    inputValue: def,
    showCancelButton: true,
    confirmButtonText: 'Guardar',
    cancelButtonText: 'Cancelar'
  });
  return value;
};

/* Toast reutilizable */
window.SwalToast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 2200,
  timerProgressBar: true
});
window.toast = (title, icon = 'success', ms = 2200) =>
  window.SwalToast.fire({ icon, title, timer: ms });

/* Loading estándar */
window.swalLoading = (titulo = 'Procesando…') =>
  Swal.fire({ title: titulo, allowOutsideClick: false, allowEscapeKey: false, didOpen: () => Swal.showLoading() });

/* ===================== Tema (light/dark) ===================== */
function getSystemPrefersDark() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}
function applyTheme(theme) {
  const body = document.body;
  const btn = document.getElementById('toggleDark');

  if (theme === 'dark' && ALLOW_DARK) {
    body.classList.add('dark');
    if (btn) {
      btn.disabled = false;
      btn.setAttribute('aria-pressed', 'true');
      const i = btn.querySelector('i');
      if (i) { i.classList.remove('fa-moon'); i.classList.add('fa-sun'); }
      btn.title = 'Cambiar a modo claro';
    }
  } else {
    body.classList.remove('dark');
    if (btn) {
      btn.setAttribute('aria-pressed', 'false');
      const i = btn.querySelector('i');
      if (i) { i.classList.remove('fa-sun'); i.classList.add('fa-moon'); }
      btn.title = ALLOW_DARK ? 'Cambiar a modo oscuro' : 'Modo oscuro deshabilitado';
      if (!ALLOW_DARK) btn.disabled = true;
    }
  }
}
function initTheme() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    let theme = 'light';
    if (!ALLOW_DARK) {
      theme = 'light';
      localStorage.removeItem(THEME_STORAGE_KEY);
    } else {
      theme = (saved === 'light' || saved === 'dark') ? saved : (getSystemPrefersDark() ? 'dark' : 'light');
    }
    applyTheme(theme);
  } catch { applyTheme('light'); }
}
function toggleTheme() {
  if (!ALLOW_DARK) return;
  const isDark = document.body.classList.contains('dark');
  const next = isDark ? 'light' : 'dark';
  try { localStorage.setItem(THEME_STORAGE_KEY, next); } catch (_) { /* no-op */ }
  applyTheme(next);
}

/* ========= Flashes de Flask -> SweetAlert2 ========= */
document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('flash-data');
  let flashes = [];
  if (el) {
    try { flashes = JSON.parse(el.textContent || '[]'); }
    catch (e) { console.warn('[flash] JSON inválido en #flash-data:', e); flashes = []; }
  }
  if (Array.isArray(flashes) && flashes.length) {
    const iconFor = (cat) => {
      const c = String(cat || '').toLowerCase();
      if (c === 'danger' || c === 'error') return 'error';
      if (c === 'warning' || c === 'warn') return 'warning';
      if (c === 'success' || c === 'ok') return 'success';
      return 'info';
    };
    flashes.forEach(([cat, msg]) => {
      window.SwalToast.fire({ icon: iconFor(cat), title: String(msg) });
    });
  }
});

/* ========= Inicializaciones UI globales ========= */
document.addEventListener('DOMContentLoaded', () => {
  // Tema
  initTheme();
  const toggleBtn = document.getElementById('toggleDark');
  if (toggleBtn) toggleBtn.addEventListener('click', toggleTheme);

  // Localización de Flatpickr
  if (window.flatpickr) flatpickr.localize(flatpickr.l10ns.es);

  // Sidebar en móvil: abrir/cerrar y click fuera (robusto)
(() => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('btnToggleSidebar');
  if (!sidebar || !toggle) return;

  const mql = window.matchMedia('(max-width: 991.98px)');
  const isMobile = () => mql.matches;

  const open = () => {
    sidebar.classList.add('show');
    toggle.setAttribute('aria-expanded', 'true');
  };
  const close = () => {
    sidebar.classList.remove('show');
    toggle.setAttribute('aria-expanded', 'false');
  };
  const toggleSidebar = (ev) => {
    if (!isMobile()) return;
    ev.preventDefault();
    // muy importante: que el click del botón NO dispare el “cerrar por fuera”
    ev.stopPropagation();
    ev.stopImmediatePropagation?.();
    sidebar.classList.toggle('show');
    toggle.setAttribute('aria-expanded', sidebar.classList.contains('show') ? 'true' : 'false');
  };

  // accesibilidad
  toggle.setAttribute('aria-controls', 'sidebar');
  toggle.setAttribute('aria-expanded', 'false');

  // abrir/cerrar con el botón
  toggle.addEventListener('click', toggleSidebar);
  // en móviles, algunos navegadores disparan "pointerdown" antes que "click"
  toggle.addEventListener('pointerdown', (e) => {
    // evitar que el “click fuera” lo capture en la misma interacción
    e.stopPropagation();
  });

  // cerrar al tocar/click fuera (capturando para ser el primero en ejecutar)
  document.addEventListener('pointerdown', (e) => {
    if (!isMobile()) return;
    if (sidebar.contains(e.target) || toggle.contains(e.target)) return;
    close();
  }, true);

  // cerrar con Esc
  document.addEventListener('keydown', (e) => {
    if (isMobile() && e.key === 'Escape') close();
  });

  mql.addEventListener?.('change', () => {
    if (!isMobile()) close();
  });
})();


  // Autoabrir colapsables que contengan un link activo
  document.querySelectorAll('.submenu .collapse').forEach(col => {
    if (col.querySelector('a.active')) {
      new bootstrap.Collapse(col, { toggle: true });
      const b = col.previousElementSibling;
      if (b && b.matches('button[aria-expanded]')) b.setAttribute('aria-expanded', 'true');
    }
  });

  // Actualiza cuando cambia el sistema (si se permite dark y no hay preferencia guardada)
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  if (ALLOW_DARK && media?.addEventListener) {
    media.addEventListener('change', () => {
      try {
        if (!localStorage.getItem(THEME_STORAGE_KEY)) {
          applyTheme(getSystemPrefersDark() ? 'dark' : 'light');
        }
      } catch (_) { /* no-op */ }
    });
  }
});


(function(){
  document.addEventListener('click', function(ev){
    const btn = ev.target.closest('[data-bs-toggle="collapse"]');
    if (!btn) return;

    // Evita navegación por href y bloquea handlers de Bootstrap/data-API (doble toggle)
    ev.preventDefault();
    ev.stopPropagation();
    ev.stopImmediatePropagation();

    const selector = btn.getAttribute('data-bs-target') || btn.getAttribute('href');
    if (!selector || !selector.startsWith('#')) return;

    const target = document.querySelector(selector);
    if (!target) return;

    const inst = bootstrap.Collapse.getOrCreateInstance(target, { toggle: false });
    inst.toggle();
    
    const nowOpen = target.classList.contains('show');
    btn.setAttribute('aria-expanded', nowOpen ? 'true' : 'false');
  }, true);
})();
