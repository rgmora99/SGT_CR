/* ==================== util: fetch + helpers ==================== */
async function fetchJSON(url, opts = {}) {
  const r = await fetch(url, {
    cache: 'no-store',
    headers: { 'Accept': 'application/json', ...(opts.headers || {}) },
    ...opts
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok || (data && data.ok === false)) {
    const msg = (data && (data.mensaje || data.error)) || ('HTTP ' + r.status);
    throw new Error(msg);
  }
  return data;
}

const debounce = (fn, ms = 400) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

// ---- SweetAlert2: toast seguro + helper notify ----
const toast = (typeof Swal !== 'undefined' && Swal.mixin) ? Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 4000,
  timerProgressBar: true,
}) : null;

function notify(icon, title) {
  if (toast) {
    toast.fire({ icon, title });
  } else if (window.swalWarn && icon !== 'success') {
    swalWarn('Aviso', title);
  } else if (window.swalOk && icon === 'success') {
    swalOk('Listo', title);
  } else {
    alert(title);
  }
}

/* ========== Error helper (SweetAlert2) ========== */
/* ========== Error helper (SweetAlert2) ========== */
function handleErr(e, fallback = 'Ocurrió un error') {
  const raw = (e && e.message) ? String(e.message) : String(fallback);
  const low = raw.toLowerCase();

  // Mensaje específico cuando el usuario no existe / no está logueado
  const usuarioNoValido =
    /usuario\s*(no|incorrecto|inexistente)|no\s*encontrado|no\s*existe|no\s*logueado|sin\s*coincidencias/.test(low);

  const msg = usuarioNoValido
    ? 'Usuario incorrecto o no loggeado al sistema, por favor pruebe con otro'
    : raw;

  if (window.swalErr) swalErr('Error', msg);
  else alert(msg);
}

/* ==================== Guardas de inicialización ==================== */
const INIT_GUARD = {
  repUsr: false,
  repRol: false,
  usuariosRolBtn: false,
};

/* ==================== UI helpers (checkbox lists) ==================== */
function renderCheckboxList(container, items, checkedSet, idKey, labelKey) {
  container.innerHTML = '';
  if (!items || !items.length) {
    container.innerHTML = "<div class='text-muted small px-2 py-1'>No hay reportes para mostrar.</div>";
    return;
  }
  items.forEach(it => {
    const id = it[idKey];
    const base = it[labelKey] || String(id);

    const div = document.createElement('div');
    div.className = 'form-check';

    const input = document.createElement('input');
    input.type = 'checkbox';
    input.className = 'form-check-input';
    input.id = `chk_${container.id}_${id}`;
    input.value = id;
    input.checked = checkedSet.has(id);

    const label = document.createElement('label');
    label.className = 'form-check-label';
    label.setAttribute('for', input.id);
    label.textContent = base;

    div.appendChild(input);
    div.appendChild(label);
    container.appendChild(div);
  });
}

function getCheckedIds(container) {
  return Array.from(container.querySelectorAll('.form-check-input:checked')).map(cb => parseInt(cb.value, 10));
}
function updateCount(container, labelId) {
  const lbl = document.getElementById(labelId);
  if (!lbl) return;
  const n = container.querySelectorAll('.form-check-input:checked').length;
  lbl.textContent = String(n);
}
function setAllIn(container, checked, labelId) {
  container.querySelectorAll('.form-check-input').forEach(cb => (cb.checked = checked));
  updateCount(container, labelId);
}

// --- Aviso unificado para búsquedas de usuarios ---
function showSearchHint() {
  return (window.swalWarn?.('Buscar usuario', 'Escribe correo, nombre o código para buscar.'))
         || alert('Escribe correo, nombre o código para buscar.');
}

/* ==================== filtro (expuesto a window para onkeyup) ==================== */
function filtrarReportes(containerId, texto) {
  const cont = document.getElementById(containerId);
  if (!cont) return;
  const q = (texto || '').toLowerCase();
  cont.querySelectorAll('.form-check').forEach(div => {
    const label = div.querySelector('label');
    const show = label && label.textContent.toLowerCase().includes(q);
    div.style.display = show ? '' : 'none';
  });
}
window.filtrarReportes = filtrarReportes;

/* ==================== CRUD de roles ==================== */
function validarNombreDesc(nombre, descripcion) {
  const reNombre = /^[A-Za-z0-9 _\-áéíóúÁÉÍÓÚñÑ]{3,50}$/;
  const reDesc   = /^[A-Za-z0-9 _\-\.,;:()¿?¡!áéíóúÁÉÍÓÚñÑ]{1,50}$/;

  if (!nombre || !reNombre.test(nombre.trim())) {
    throw new Error("Nombre inválido. (No admite carácteres especiales, espacios en blanco, exceso de cifras).");
  }
  if (!descripcion || !reDesc.test(descripcion.trim())) {
    throw new Error("Descripción inválida. (No admite carácteres especiales, espacios en blanco, exceso de cifras).");
  }
}


// === Modal crear/editar rol (mismo diseño) ===
let currentRolId = null;

async function openRoleModal(mode, id = null) {
  const modalEl = document.getElementById('roleModal');
  const modal   = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
  const titleEl = document.getElementById('roleModalTitle');
  const btn     = document.getElementById('btnSubmitRol');

  // reset
  document.getElementById('roleForm')?.reset();
  document.getElementById('rol_id').value = '';
  currentRolId = null;

  if (mode === 'create') {
    titleEl.textContent = 'Crear nuevo rol';
    btn.textContent = 'Guardar';
    modal.show();
    return;
  }

  // editar
  titleEl.textContent = 'Editar rol';
  btn.textContent = 'Actualizar';
  currentRolId = Number(id);
  document.getElementById('rol_id').value = currentRolId;

  const data = await fetchJSON(`/rol/api/roles/${currentRolId}`);
  document.getElementById('nombreRol').value      = data.nombre || '';
  document.getElementById('descripcionRol').value = data.descripcion || '';
  modal.show();
}

/*async function editarRol(id) {
  try {
    const nuevoNombre = await swalPrompt('Nuevo nombre del rol', '', '');
    if (nuevoNombre == null) return;
    const nuevaDesc   = await swalPrompt('Nueva descripción del rol', '', '') ?? '';

    await fetchJSON(`/rol/api/roles/${id}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ nombre: String(nuevoNombre).trim(), descripcion: String(nuevaDesc).trim() })
    });

    swalOk('¡Listo!', 'Rol actualizado');
    setTimeout(() => location.reload(), 600);
  } catch (e) {
    handleErr(e, 'No se pudo actualizar el rol');
  }
}*/
async function eliminarRol(id) {
  try {
    const ok = await swalAsk('Eliminar rol', 'Esta acción no se puede deshacer. ¿Continuar?');
    if (!ok.isConfirmed) return;

    await fetchJSON(`/rol/api/roles/${id}`, { method: 'DELETE' });
    swalOk('Eliminado', 'Rol eliminado correctamente');
    setTimeout(() => location.reload(), 600);
  } catch (e) {
    handleErr(e, 'No se pudo eliminar el rol');
  }
}
async function verUsuariosDeRol(id) {
  try {
    const data = await fetchJSON(`/rol/usuarios_por_rol?rol=${encodeURIComponent(id)}`);
    const lista = document.getElementById("listaUsuariosRol");
    if (!lista) return;

    lista.innerHTML = "";
    if (!Array.isArray(data) || !data.length) {
      lista.innerHTML = "<li class='list-group-item'>No hay usuarios con este rol.</li>";
    } else {
      data.forEach(u => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = `${u.nombre_completo} (${u.correo})`;
        lista.appendChild(li);
      });
    }

    const modalEl = document.getElementById("usuariosModal");
    if (!modalEl) { console.error("No existe #usuariosModal en el DOM"); return; }
    const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
    modal.show();
  } catch (err) {
    handleErr(err, 'No se pudieron cargar los usuarios de este rol');
  }
}

document.addEventListener('click', (e) => {
  const btnEdit = e.target.closest('.btn-edit-rol');
  if (btnEdit) { openRoleModal('edit', btnEdit.dataset.rolId); return; }

  const btnDel = e.target.closest('.btn-del-rol');
  if (btnDel) { eliminarRol(btnDel.dataset.rolId); return; }

  const btnUsers = e.target.closest('.btn-users-rol');
  if (btnUsers) { verUsuariosDeRol(btnUsers.dataset.rolId); return; }
});

function clearUsuarioYRoles() {
  const sel = document.getElementById('selectUsuario');
  if (sel) {
    sel.value = '';
    sel.innerHTML = ''; // vacía la lista para que no quede el usuario previo
  }
  renderRolesAsignados([]); // ya la tienes definida
}



/* ==================== Asignación de roles a usuarios ==================== */
function renderRolesAsignados(roles) {
  const box = document.getElementById('contenedorRolesUsuario');
  if (!box) return;
  box.innerHTML = '';
  if (!roles || !roles.length) {
    box.innerHTML = '<span class="badge bg-secondary">Sin roles</span>';
    return;
  }
  roles.forEach(r => {
    const pill = document.createElement('span');
    pill.className = 'badge bg-info d-flex align-items-center gap-2';
    pill.style.cursor = 'default';
    pill.textContent = r.nombre + ' ';

    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-light ms-1';
    btn.setAttribute('data-remove-role', r.id);
    btn.setAttribute('title', 'Quitar');
    btn.type = 'button';
    btn.textContent = '×';

    pill.appendChild(btn);
    box.appendChild(pill);
  });
}
async function cargarRolesDisponibles() {
  const sel = document.getElementById('rolesSelect');
  if (!sel) return;
  sel.innerHTML = '';
  const roles = await fetchJSON('/rol/api/roles');
  roles.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r.id;
    opt.textContent = r.nombre;
    sel.appendChild(opt);
  });

  const rolFiltro = document.getElementById('rolFiltro');
  if (rolFiltro) {
    rolFiltro.innerHTML = '<option value="" selected disabled>Seleccione</option>';
    roles.forEach(r => {
      const opt = document.createElement('option');
      opt.value = r.nombre; // endpoint acepta id o nombre
      opt.textContent = r.nombre;
      rolFiltro.appendChild(opt);
    });
  }
}

async function buscarUsuarios() {
  const q = (document.getElementById('inputBuscarUsuario')?.value || '').trim();
  const sel = document.getElementById('selectUsuario');
  if (!sel) return;

  if (!q) {
    // si está vacío: limpiar todo y salir
    clearUsuarioYRoles();
    showSearchHint();
    return;
  }

  try {
    sel.innerHTML = '';
    const res = await fetchJSON(`/rol/api/usuarios?q=${encodeURIComponent(q)}&limit=25`);
    const usuarios = (res && res.usuarios) || [];

    if (!usuarios.length) {
      // sin coincidencias: limpiar roles/selector y mostrar mensaje
      clearUsuarioYRoles();
      notify('error', 'Usuario incorrecto o no loggeado al sistema, por favor pruebe con otro');
      // opcional: añade una opción muerta para que el select no quede “con el anterior”
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Sin coincidencias';
      sel.appendChild(opt);
      return;
    }

    // hay resultados: primero asegura deseleccionar el anterior
    sel.value = '';
    const opt0 = document.createElement('option');
    opt0.value = '';
    opt0.textContent = 'Seleccione un usuario…';
    sel.appendChild(opt0);

    usuarios.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = `${u.nombre_completo} — ${u.correo}`;
      sel.appendChild(opt);
    });

    if (usuarios.length === 1) {
      sel.selectedIndex = 1; // selecciona el único usuario
      await cargarRolesDeUsuarioActual();
    } else {
      // múltiples: limpia roles hasta que elijan uno
      renderRolesAsignados([]);
    }
  } catch (e) {
    clearUsuarioYRoles();
    handleErr(e, 'Error al buscar usuarios');
  }
}

let currentRolesReqId = 0;  // ponlo en el mismo scope que la función

async function cargarRolesDeUsuarioActual() {
  const sel = document.getElementById('selectUsuario');
  if (!sel || !sel.value) { renderRolesAsignados([]); return; }

  const reqId = ++currentRolesReqId;
  try {
    const data = await fetchJSON(`/rol/api/usuario_roles/${sel.value}`);
    if (reqId !== currentRolesReqId) return; // llegó tarde: ignorar
    renderRolesAsignados((data && data.roles) || []);
  } catch (e) {
    if (reqId === currentRolesReqId) renderRolesAsignados([]);
    handleErr(e, 'No se pudieron cargar los roles del usuario');
  }
}


async function asignarRolesSeleccionados() {
  const selUsr = document.getElementById('selectUsuario');
  const selRoles = document.getElementById('rolesSelect');
  if (!selUsr || !selUsr.value) { swalWarn('Seleccione un usuario', 'Debe elegir un usuario de la lista.'); return; }
  const roles = Array.from(selRoles.selectedOptions).map(o => parseInt(o.value, 10));
  if (!roles.length) { swalWarn('Sin roles', 'Seleccione al menos un rol.'); return; }

  try {
    await fetchJSON('/rol/api/usuario_roles', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ usuario_id: parseInt(selUsr.value, 10), roles })
    });
    await cargarRolesDeUsuarioActual();
    swalOk('¡Listo!', 'Roles asignados');
  } catch (e) {
    handleErr(e, 'No se pudo asignar roles');
  }
}
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('button[data-remove-role]');
  if (!btn) return;
  e.preventDefault();

  const rolId = parseInt(btn.getAttribute('data-remove-role'), 10);
  const selUsr = document.getElementById('selectUsuario');
  if (!selUsr || !selUsr.value) return;

  const ok = await swalAsk('Quitar rol', '¿Desea quitar este rol del usuario?');
  if (!ok.isConfirmed) return;

  try {
    await fetchJSON('/rol/api/usuario_roles', {
      method: 'DELETE',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ usuario_id: parseInt(selUsr.value, 10), rol_id: rolId })
    });
    await cargarRolesDeUsuarioActual();
    notify('success', 'Rol removido');

  } catch (e2) {
    handleErr(e2, 'No se pudo quitar el rol');
  }
});

/* ==================== Permisos por rol ==================== */
function getPermCheckboxes() {
  return Array.from(document.querySelectorAll('input[name="permisos"]'));
}
function setCheckedPerms(ids = []) {
  const set = new Set(ids.map(Number));
  getPermCheckboxes().forEach(cb => { cb.checked = set.has(Number(cb.value)); });
  updatePermCount();
}
function updatePermCount() {
  const count = getPermCheckboxes().filter(cb => cb.checked).length;
  const lbl = document.getElementById('permCount');
  if (lbl) lbl.textContent = String(count);
}
async function cargarPermisosDeRol(rolId) {
  if (!rolId) { setCheckedPerms([]); return; }
  try {
    const data = await fetchJSON(`/rol/permisos/${encodeURIComponent(rolId)}`);
    const ids = (data && data.permisos) || [];
    setCheckedPerms(ids);
  } catch (err) {
    handleErr(err, 'No se pudieron cargar permisos del rol');
  }
}

/* ==================== Reportes (catálogo y cache) ==================== */
const CACHE_REP = { catalogo: null, asignadosRol: {}, asignadosUsr: {}, _byKey: {} };

// etiqueta “limpia” para evitar repeticiones (nombre — descripcion)
function makeReporteLabel(nombre, descripcion) {
  const parts = [String(nombre || '').trim()];
  const desc = String(descripcion || '').trim();
  if (desc && desc.toLowerCase() !== parts[0].toLowerCase()) parts.push(desc);
  const cleaned = [];
  for (const p of parts.join(' — ').split('—')) {
    const t = p.trim();
    if (t && !cleaned.map(c => c.toLowerCase()).includes(t.toLowerCase())) cleaned.push(t);
  }
  return cleaned.join(' — ');
}

// Limpia caché (por si cambias de sección o de contexto)
function invalidateCatalogoReportesCache() {
  if (CACHE_REP && CACHE_REP._byKey) CACHE_REP._byKey = {};
}

/**
 * Carga catálogo de reportes.
 * opts:
 *   - usuarioId: number | null   (si se envía, el backend valida gerencia y filtra acorde)
 *   - q: string                  (búsqueda server-side)
 *   - forceReload: boolean       (ignora caché)
 */
async function cargarCatalogoReportes(opts = {}) {
  const usuarioId  = opts.usuarioId ? Number(opts.usuarioId) : null;
  const q          = (opts.q || '').trim();
  const force      = !!opts.forceReload;

  const key = `uid=${usuarioId ?? 'all'}&q=${q.toLowerCase()}`;

  if (!force && CACHE_REP._byKey[key]) {
    return CACHE_REP._byKey[key];
  }

  const params = new URLSearchParams();
  if (usuarioId) params.set('usuario_id', String(usuarioId));
  if (q)         params.set('q', q);

  try {
    const url = `/rol/api/reportes${params.toString() ? `?${params.toString()}` : ''}`;
    const res = await fetchJSON(url);

    // Soporta { ok:true, reportes:[...] } o lista directa
    const listaCruda = (res?.reportes ?? res ?? []);
    const lista = listaCruda.map(r => ({
      id: Number(r.id),
      nombre: r.nombre,
      descripcion: r.descripcion || '',
      label: makeReporteLabel(r.nombre, r.descripcion),
    }));

    CACHE_REP._byKey[key] = lista;
    return lista;
  } catch (e) {
    // Si el backend devuelve 403 (coordinador vs. gerencia), no rompemos UI.
    console.warn('cargarCatalogoReportes error:', e.message || e);
    return [];
  }
}


/* ---- Reportes por ROL (sección 5) ---- */
async function initReportesPorRol() {
  if (INIT_GUARD.repRol) return;
  INIT_GUARD.repRol = true;

  const selRol = document.getElementById('rolReporteSelect');
  const cont   = document.getElementById('checkReportesRol');
  if (!selRol || !cont) return;

  if (selRol.options.length <= 1) {
    try {
      const roles = await fetchJSON('/rol/api/roles');
      selRol.innerHTML = '<option selected disabled>Seleccione un rol</option>';
      roles.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.id;
        opt.textContent = r.nombre;
        selRol.appendChild(opt);
      });
    } catch (e) { console.warn('No se pudieron cargar roles para reportes:', e.message); }
  }

  const reportes = await cargarCatalogoReportes();
  renderCheckboxList(cont, reportes, new Set(), 'id', 'label');
  updateCount(cont, 'repRolCount');

  selRol.addEventListener('change', async () => {
    const rolId = parseInt(selRol.value, 10);
    if (!rolId) return;
    try {
      const data = await fetchJSON(`/rol/api/reportes_rol/${rolId}`);
      const set = new Set((data.reportes || []).map(x => Number(x.id)));
      CACHE_REP.asignadosRol[rolId] = set;
      renderCheckboxList(cont, reportes, set, 'id', 'label');
      updateCount(cont, 'repRolCount');
    } catch (e) {
      handleErr(e, 'No se pudieron cargar los reportes del rol');
    }
  });

  document.getElementById('btnRepRolTodos')?.addEventListener('click', () => setAllIn(cont, true, 'repRolCount'));
  document.getElementById('btnRepRolNinguno')?.addEventListener('click', () => setAllIn(cont, false, 'repRolCount'));
  cont.addEventListener('change', () => updateCount(cont, 'repRolCount'));

  const form = selRol.closest('form');
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const rolId = parseInt(selRol.value, 10);
    if (!rolId) return swalWarn('Falta rol', 'Seleccione un rol.');

    const prev = CACHE_REP.asignadosRol[rolId] || new Set();
    const now  = new Set(getCheckedIds(cont));
    const toAdd    = [...now].filter(id => !prev.has(id));
    const toRemove = [...prev].filter(id => !now.has(id));

    try {
      if (toAdd.length) {
        await fetchJSON('/rol/api/reportes_rol', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ rol_id: rolId, reportes: toAdd })
        });
      }
      for (const repId of toRemove) {
        await fetchJSON('/rol/api/reportes_rol', {
          method: 'DELETE',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ rol_id: rolId, reporte_id: repId })
        });
      }
      CACHE_REP.asignadosRol[rolId] = now;
      updateCount(cont, 'repRolCount');
      swalOk('¡Listo!', 'Reportes del rol actualizados.');
    } catch (e2) {
      handleErr(e2, 'Error al actualizar reportes del rol');
    }
  });
}

/* ---- Reportes por USUARIO (sección 6) ---- */
async function initReportesPorUsuario() {
  if (INIT_GUARD.repUsr) return;
  INIT_GUARD.repUsr = true;

  const input   = document.getElementById('buscarUsuario');        // buscador de usuarios
  const btn     = document.getElementById('btnBuscarUsuarioRep');  // botón buscar usuario
  const selUsr  = document.getElementById('usuarioReporteSelect'); // select de usuarios
  const cont    = document.getElementById('checkReportesUsuario'); // contenedor de checks
  if (!input || !selUsr || !cont) return;

  // opcional: input de búsqueda de reportes (placeholder “Buscar reporte…”)
  const inputBuscarReporte = document.getElementById('inputBuscarReporte');
  const getQ = () => (inputBuscarReporte?.value || '').trim();

  let currentUsuarioId = null;

  const pintarCatalogo = async () => {
    const reportes = await cargarCatalogoReportes({ usuarioId: currentUsuarioId, q: getQ() });
    const set = (currentUsuarioId && CACHE_REP.asignadosUsr[currentUsuarioId])
      ? CACHE_REP.asignadosUsr[currentUsuarioId]
      : new Set();
    renderCheckboxList(cont, reportes, set, 'id', 'label');
    updateCount(cont, 'repUsrCount');
  };

  const doSearch = async () => {
    const q = (input.value || '').trim();
    if (!q) return showSearchHint();
    try {
      selUsr.innerHTML = '<option selected disabled>Seleccione un usuario</option>';
      const data = await fetchJSON(`/rol/api/usuarios?q=${encodeURIComponent(q)}`);
      (data.usuarios || []).forEach(u => {
        const opt = document.createElement('option');
        opt.value = u.id;
        opt.textContent = `${u.nombre_completo} - (${u.correo})`;
        selUsr.appendChild(opt);
      });
      if ((data.usuarios || []).length === 0) {
        notify('error', 'Usuario incorrecto o no loggeado al sistema, por favor pruebe con otro');
      }
    } catch (e) {
      handleErr(e, 'Error al buscar usuarios');
    }
  };

  // eventos
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doSearch(); } });
  btn?.addEventListener('click', doSearch);

  selUsr.addEventListener('change', async () => {
    const uid = parseInt(selUsr.value, 10);
    if (!uid) return;
    currentUsuarioId = uid;
    try {
      // trae lo ya asignado (sigue validando gerencia en backend)
      const data = await fetchJSON(`/rol/api/reportes_usuario/${uid}`);
      CACHE_REP.asignadosUsr[uid] = new Set((data.reportes || []).map(x => Number(x.id)));

      // aquí forzamos a recargar el catálogo desde el backend
      const list = await cargarCatalogoReportes({ usuarioId: currentUsuarioId, q: getQ(), forceReload: true });
      renderCheckboxList(cont, list, CACHE_REP.asignadosUsr[uid], 'id', 'label');
      updateCount(cont, 'repUsrCount');
    } catch (e) {
      (window.swalWarn?.('Sin acceso', e.message || 'No autorizado.')) || alert(e.message || 'No autorizado.');
    }
  });


  // check helpers
  document.getElementById('btnRepUsrTodos')?.addEventListener('click', () => setAllIn(cont, true, 'repUsrCount'));
  document.getElementById('btnRepUsrNinguno')?.addEventListener('click', () => setAllIn(cont, false, 'repUsrCount'));
  cont.addEventListener('change', () => updateCount(cont, 'repUsrCount'));

  // si hay buscador de reportes, refresca servidor (no solo filtro client-side)
  inputBuscarReporte?.addEventListener('input', debounce(async () => {
    const list = await cargarCatalogoReportes({ usuarioId: currentUsuarioId, q: getQ(), forceReload: true });
    const set  = (currentUsuarioId && CACHE_REP.asignadosUsr[currentUsuarioId])
      ? CACHE_REP.asignadosUsr[currentUsuarioId]
      : new Set();
    renderCheckboxList(cont, list, set, 'id', 'label');
    updateCount(cont, 'repUsrCount');
  }, 300));

  // submit asignación
  const form = selUsr.closest('form');
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const uid = parseInt(selUsr.value, 10);
    if (!uid) return swalWarn('Seleccione un usuario', 'Debes elegir un usuario antes de continuar.');

    const prev = CACHE_REP.asignadosUsr[uid] || new Set();
    const now  = new Set(getCheckedIds(cont));
    const toAdd    = [...now].filter(id => !prev.has(id));
    const toRemove = [...prev].filter(id => !now.has(id));

    try {
      if (toAdd.length) {
        await fetchJSON('/rol/api/reportes_usuario', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ usuario_id: uid, reportes: toAdd })
        });
      }
      for (const repId of toRemove) {
        await fetchJSON('/rol/api/reportes_usuario', {
          method: 'DELETE',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ usuario_id: uid, reporte_id: repId })
        });
      }
      CACHE_REP.asignadosUsr[uid] = now;
      updateCount(cont, 'repUsrCount');
      (window.swalOk?.('Listo', 'Reportes del usuario actualizados.')) || alert('Reportes actualizados.');
    } catch (e2) {
      (window.swalErr?.('Error', e2.message)) || alert(`Error: ${e2.message}`);
    }
  });

  // pinta catálogo al cargar la sección (admin ve todo; coordinador, su gerencia)
  await pintarCatalogo();
}

/* ==================== Usuarios por ROL (botón “Ver Usuarios”) ==================== */
function initUsuariosPorRolBoton() {
  if (INIT_GUARD.usuariosRolBtn) return;
  INIT_GUARD.usuariosRolBtn = true;

  const btn = document.getElementById('btnVerUsuariosRol');
  const sel = document.getElementById('rolFiltro');
  if (!btn || !sel) return;

  btn.addEventListener('click', async () => {
    const val = (sel.value || '').trim();
    if (!val) { swalWarn('Seleccione un rol', 'Debes elegir un rol para listar sus usuarios.'); return; }
    try {
      const data = await fetchJSON(`/rol/usuarios_por_rol?rol=${encodeURIComponent(val)}`);
      const lista = document.getElementById("listaUsuariosRol");
      if (!lista) return;
      lista.innerHTML = "";
      if (!Array.isArray(data) || !data.length) {
        lista.innerHTML = "<li class='list-group-item'>No hay usuarios con este rol.</li>";
      } else {
        data.forEach(u => {
          const li = document.createElement("li");
          li.className = "list-group-item";
          li.textContent = `${u.nombre_completo} (${u.correo})`;
          lista.appendChild(li);
        });
      }
      const modalEl = document.getElementById("usuariosModal");
      const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
      modal.show();
    } catch (e) {
      handleErr(e, 'No se pudieron cargar usuarios del rol');
    }
  });
}

/* ==================== Permisos por rol (ENVIAR) ==================== */
function initGuardarPermisosRol() {
  const form = document.getElementById('formPermisosRol');
  const sel  = document.getElementById('rolPermisoSelect');
  if (!form || !sel) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const rolId = parseInt(sel.value || '0', 10);
    if (!rolId) { swalWarn('Falta rol', 'Seleccione un rol.'); return; }

    const ids = getPermCheckboxes()
      .filter(cb => cb.checked)
      .map(cb => parseInt(cb.value, 10));

    try {
      await fetchJSON('/rol/permisos/guardar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ rol_id: rolId, permisos: ids })
      });
      swalOk('¡Listo!', 'Permisos actualizados correctamente');
    } catch (e2) {
      handleErr(e2, 'No se pudieron guardar los permisos');
    }
  });
}

/* ==================== boot / listeners globales ==================== */
document.addEventListener('DOMContentLoaded', async () => {
  // Roles + asignación de roles
  await cargarRolesDisponibles();
  document.getElementById('btnBuscarUsuario')?.addEventListener('click', buscarUsuarios);
  document.getElementById('inputBuscarUsuario')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); buscarUsuarios(); }
  });
  document.getElementById('inputBuscarUsuario')?.addEventListener('input', debounce((ev) => {
  if (!(ev.target.value || '').trim()) {
    // si borran el texto, limpia inmediatamente
    clearUsuarioYRoles();
  }
}, 250));

  document.getElementById('selectUsuario')?.addEventListener('change', cargarRolesDeUsuarioActual);
  document.getElementById('btnAsignarRol')?.addEventListener('click', async (e) => {
    e.preventDefault();
    await asignarRolesSeleccionados();
  });

  // Permisos por rol (cargar & guardar)
  const selRolPerm = document.getElementById('rolPermisoSelect');
  if (selRolPerm) {
    selRolPerm.addEventListener('change', () => cargarPermisosDeRol(selRolPerm.value));
    if (selRolPerm.value) cargarPermisosDeRol(selRolPerm.value);
  }
  initGuardarPermisosRol();
  getPermCheckboxes().forEach(cb => cb.addEventListener('change', updatePermCount));
  updatePermCount();
  document.getElementById('btnPermTodos')?.addEventListener('click', () => { 
    getPermCheckboxes().forEach(cb => (cb.checked = true)); 
    updatePermCount(); 
  });
  document.getElementById('btnPermNinguno')?.addEventListener('click', () => { 
    getPermCheckboxes().forEach(cb => (cb.checked = false)); 
    updatePermCount(); 
  });

  // Reportes
  try {
    await initReportesPorRol();
    await initReportesPorUsuario();
  } catch (e) { console.error(e); }

  // Usuarios por ROL (btn)
  initUsuariosPorRolBoton();

  // Nuevo rol => abrir el MISMO modal en modo crear
  document.getElementById('btnNuevoRol')
    ?.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      openRoleModal('create');
    });

  // Guardar/Actualizar (POST o PUT según haya id)
  document.getElementById('btnSubmitRol')?.addEventListener('click', async () => {
    const nombre = (document.getElementById('nombreRol')?.value || '').trim();
    const descripcion = (document.getElementById('descripcionRol')?.value || '').trim();
    try { validarNombreDesc(nombre, descripcion); }
    catch (e) { return (window.swalWarn?.('Validación', e.message)) || alert(e.message); }

    const id = document.getElementById('rol_id').value;
    const isEdit = !!id;
    const url = isEdit ? `/rol/api/roles/${id}` : '/rol/api/roles';
    const method = isEdit ? 'PUT' : 'POST';

    await fetchJSON(url, {
      method,
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ nombre, descripcion })
    });

    (window.swalOk?.('¡Listo!', isEdit ? 'Rol actualizado' : 'Rol creado')) || alert('OK');
    bootstrap.Modal.getInstance(document.getElementById('roleModal')).hide();
    setTimeout(() => location.reload(), 500);
  });

  /* ==================== Paginación de Roles (client-side) ==================== */
  (function attachRolesPagination() {
    function init() {
      try {
        const ROWS_PER_PAGE = 5;
        const tbody = document.getElementById('rolesTbody');
        const pager = document.getElementById('rolesPagination');
        const footer = pager ? pager.closest('.card-footer') : null;

        if (!tbody || !pager) return; 

        function paginateRows(rows, page, perPage) {
          const start = (page - 1) * perPage;
          const end = start + perPage;
          rows.forEach((tr, i) => { tr.style.display = (i >= start && i < end) ? '' : 'none'; });
        }

        function buildPager(totalRows, perPage, currentPage) {
          const totalPages = Math.max(1, Math.ceil(totalRows / perPage));
          pager.innerHTML = '';

          // Mostrar/ocultar footer si hace falta
          if (footer) footer.style.display = (totalPages > 1 ? '' : 'none');

          const makeLi = (label, disabled, active, onClick) => {
            const li = document.createElement('li');
            li.className = 'page-item' + (disabled ? ' disabled' : '') + (active ? ' active' : '');
            li.innerHTML = `<a class="page-link" href="#">${label}</a>`;
            if (!disabled) li.onclick = (e) => { e.preventDefault(); onClick(); };
            return li;
          };

          pager.appendChild(makeLi('«', currentPage === 1, false, () => setPage(currentPage - 1)));
          for (let p = 1; p <= totalPages; p++) {
            pager.appendChild(makeLi(String(p), false, p === currentPage, () => setPage(p)));
          }
          pager.appendChild(makeLi('»', currentPage === totalPages, false, () => setPage(currentPage + 1)));
        }

        let currentPage = 1;

        function setPage(p) {
          const rows = Array.from(tbody.querySelectorAll('tr'));
          const totalRows = rows.length;
          const totalPages = Math.max(1, Math.ceil(totalRows / ROWS_PER_PAGE));
          currentPage = Math.min(Math.max(1, p), totalPages);
          paginateRows(rows, currentPage, ROWS_PER_PAGE);
          buildPager(totalRows, ROWS_PER_PAGE, currentPage);
        }

        // Recalcular si cambian las filas (crear/editar/eliminar)
        const observer = new MutationObserver(() => setPage(currentPage));
        observer.observe(tbody, { childList: true });

        // Inicializar
        setPage(1);
      } catch (e) {
        console.error('Paginación de roles: ', e);
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  })();

  // ===================== Usuarios por Rol: Paginación + Modal Hook =====================
// ===================== Usuarios por Rol: paginación + filtro por rol + modal =====================
(() => {
  // Reuso de helpers si existen
  const _fetchJSON = (typeof fetchJSON === 'function') ? fetchJSON : async (url, opts) => {
    const r = await fetch(url, opts);
    const data = await r.json().catch(() => ({}));
    if (!r.ok || (data && data.ok === false)) {
      const msg = (data && (data.mensaje || data.error)) || ('HTTP ' + r.status);
      throw new Error(msg);
    }
    return data;
  };
  const _handleErr = (typeof handleErr === 'function') ? handleErr : (e) => console.error(e);

  // ---------- Normalizadores de campos ----------
  function nombreVisible(u) {
    // prueba varias llaves comunes
    const n =
      u.nombre?.toString().trim() ||
      u.nombre_completo?.toString().trim() ||
      u.display_name?.toString().trim() ||
      u.cn?.toString().trim() ||
      u.name?.toString().trim() ||
      // combinación de posibles partes
      [u.primer_nombre, u.segundo_nombre, u.primer_apellido, u.segundo_apellido]
        .filter(Boolean).join(' ').trim() ||
      [u.givenName, u.sn].filter(Boolean).join(' ').trim();

    return n && n.length ? n : 'Sin nombre';
  }
  function correoVisible(u) {
    return (
      u.correo ||
      u.email ||
      u.mail ||
      u.usuario_correo ||
      u.username ||
      u.usuario ||
      ''
    );
  }

  // Detección de pertenencia al rol
  function tieneRol(u, rolId, rolNombre) {
    const id = Number(rolId);
    const rid = (v) => Number(v) === id;

    // Casos comunes
    if (u.rol_id != null && rid(u.rol_id)) return true;
    if (Array.isArray(u.roles_ids) && u.roles_ids.some(rid)) return true;

    // roles como [{id, nombre}] o [id] o ["nombre"]
    if (Array.isArray(u.roles)) {
      return u.roles.some((r) => {
        if (r == null) return false;
        if (typeof r === 'number' || typeof r === 'string') {
          // coincide por id o por nombre
          return rid(r) || (rolNombre && String(r).toLowerCase() === String(rolNombre).toLowerCase());
        }
        if (typeof r === 'object') {
          return (r.id != null && rid(r.id)) ||
                 (rolNombre && r.nombre && String(r.nombre).toLowerCase() === String(rolNombre).toLowerCase());
        }
        return false;
      });
    }

    // mapa { idRol: true }
    if (u.roles_map && (u.roles_map[id] || u.roles_map[String(id)])) return true;

    // sin señal clara
    return false;
  }

  // Filtro robusto: si el backend ignoró el rol_id, filtramos aquí
  function filtrarPorRol(usuarios, rolId, rolNombre) {
    const arr = Array.isArray(usuarios) ? usuarios : [];
    const filtrados = arr.filter((u) => tieneRol(u, rolId, rolNombre));

    // Heurística:
    // - Si no encontramos ninguno pero el backend probablemente ya filtró, dejamos el array original.
    // - Si encontramos algunos, usamos los filtrados.
    if (filtrados.length > 0) return filtrados;
    return arr;
  }

  // ---------- Paginación (reuso si ya lo tenías) ----------
  const USUARIOS_ROL_PAGE_SIZE = 10;
  const usuariosRolState = { items: [], itemsOriginal: null, page: 1, pageSize: USUARIOS_ROL_PAGE_SIZE };

  function paginateArray(items, page, pageSize) {
    const total = items.length;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const current = Math.min(Math.max(1, page), totalPages);
    const start = (current - 1) * pageSize;
    const pageItems = items.slice(start, start + pageSize);
    return { total, totalPages, current, pageItems };
  }

  function buildPager(containerEl, totalPages, currentPage, onGo) {
    if (!containerEl) return;
    containerEl.innerHTML = '';

    const makeBtn = (label, page, disabled = false, active = false) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `btn btn-sm ${active ? 'btn-primary' : 'btn-outline-primary'} mx-1`;
      btn.textContent = label;
      btn.disabled = disabled || active;
      btn.addEventListener('click', () => onGo(page));
      return btn;
    };

    const prev = makeBtn('«', currentPage - 1, currentPage <= 1);
    const next = makeBtn('»', currentPage + 1, currentPage >= totalPages);
    containerEl.appendChild(prev);

    const windowSize = 5;
    let start = Math.max(1, currentPage - 2);
    let end = Math.min(totalPages, start + windowSize - 1);
    start = Math.max(1, end - windowSize + 1);

    if (start > 1) {
      containerEl.appendChild(makeBtn('1', 1, false, currentPage === 1));
      if (start > 2) containerEl.appendChild(Object.assign(document.createElement('span'), { className: 'mx-1', textContent: '…' }));
    }
    for (let p = start; p <= end; p++) containerEl.appendChild(makeBtn(String(p), p, false, p === currentPage));
    if (end < totalPages) {
      if (end < totalPages - 1) containerEl.appendChild(Object.assign(document.createElement('span'), { className: 'mx-1', textContent: '…' }));
      containerEl.appendChild(makeBtn(String(totalPages), totalPages, false, currentPage === totalPages));
    }
    containerEl.appendChild(next);
  }

  function drawUsuariosPorRol() {
    const listEl  = document.getElementById('usuariosPorRol');
    const pagerEl = document.getElementById('pagerUsuariosRol');
    if (!listEl || !pagerEl) return;

    const { items, page, pageSize } = usuariosRolState;
    const { total, totalPages, current, pageItems } = paginateArray(items, page, pageSize);

    listEl.innerHTML = '';
    if (total === 0) {
      listEl.innerHTML = `<div class="text-muted text-center py-3">No hay usuarios asignados a este rol.</div>`;
    } else {
      for (const u of pageItems) {
        const li = document.createElement('div');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `
          <div class="d-flex flex-column">
            <span class="fw-semibold">${nombreVisible(u)}</span>
            <small class="text-muted">${correoVisible(u)}</small>
          </div>
          ${u.activo === false ? '<span class="badge bg-secondary">Inactivo</span>' : ''}
        `;
        listEl.appendChild(li);
      }
    }

    buildPager(pagerEl, totalPages, current, (goTo) => {
      usuariosRolState.page = goTo;
      drawUsuariosPorRol();
    });
  }

  // API pública para rellenar
  window.renderUsuariosPorRol = function renderUsuariosPorRol(usuariosArray) {
    // dedupe por correo/usuario si vinieran duplicados
    const seen = new Set();
    const clean = [];
    for (const u of (Array.isArray(usuariosArray) ? usuariosArray : [])) {
      const key = (correoVisible(u) || nombreVisible(u)).toLowerCase();
      if (!seen.has(key)) { seen.add(key); clean.push(u); }
    }
    usuariosRolState.items = clean;
    usuariosRolState.itemsOriginal = null;
    usuariosRolState.page = 1;
    drawUsuariosPorRol();
  };

  // Enganche del botón en "Roles existentes"
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-users-rol');
    if (!btn) return;

    const rolId = btn.dataset.rolId;
    if (!rolId) return;

    // Intentar leer el nombre del rol desde la fila
    let rolNombre = '';
    const tr = btn.closest('tr');
    if (tr) {
      const tdNombre = tr.querySelector('td:nth-child(1)');
      if (tdNombre) rolNombre = (tdNombre.textContent || '').trim();
    }

    try {
      // Llama a tu endpoint. Si el backend ignora el filtro, filtramos en cliente.
      const data = await fetchJSON(`/rol/api/usuarios_por_rol?rol_id=${encodeURIComponent(rolId)}`);
      const usuariosRaw = Array.isArray(data) ? data : (data.usuarios || []);
      const usuarios = filtrarPorRol(usuariosRaw, rolId, rolNombre);

      // Título del modal con nombre del rol y cantidad
      const modalEl = document.getElementById('usuariosModal');
      const titleEl = modalEl?.querySelector('.modal-title');
      if (titleEl) {
        const total = usuarios.length;
        titleEl.innerHTML = `<i class="fas fa-users me-2"></i> Usuarios con el rol${rolNombre ? `: ${rolNombre}` : ''} (${total})`;
      }

      // Render y abrir modal
      window.renderUsuariosPorRol(usuarios);
      const modal = bootstrap && bootstrap.Modal ? new bootstrap.Modal(modalEl) : null;
      if (modal) modal.show();
      else modalEl.classList.add('show');
    } catch (err) {
      _handleErr(err);
    }
  });
})();
});
