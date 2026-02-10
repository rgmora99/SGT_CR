document.addEventListener("DOMContentLoaded", () => {
  cargarUsuarios();
  cargarRoles();
  cargarModulos();
  cargarAcciones();
});

// ==== USUARIOS ====
function cargarUsuarios() {
  fetch('/api/usuarios')
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('tblUsuarios');
      tbody.innerHTML = data.map(u => `
        <tr>
          <td>${u.nombre_completo}</td>
          <td>${u.correo}</td>
          <td>${u.roles.join(', ') || '—'}</td>
          <td>${u.ultimo_acceso || '—'}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary" onclick="abrirAsignacionRoles(${u.id})">
              <i class="bi bi-person-gear"></i>
            </button>
          </td>
        </tr>`).join('');
    });
}

function abrirAsignacionRoles(idUsuario) {
  alert("Abrir modal para asignar roles al usuario ID: " + idUsuario);
}

// ==== ROLES ====
function cargarRoles() {
  fetch('/api/roles')
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('tblRoles');
      tbody.innerHTML = data.map(r => `
        <tr>
          <td>${r.nombre}</td>
          <td>${r.descripcion || ''}</td>
          <td><span class="badge ${r.estado ? 'text-bg-success' : 'text-bg-secondary'}">
            ${r.estado ? 'Activo' : 'Inactivo'}</span></td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-info" onclick="mostrarPermisos(${r.id}, '${r.nombre}')">
              <i class="bi bi-shield-lock"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
          </td>
        </tr>`).join('');
    });
}

function mostrarPermisos(rolId, rolNombre) {
  document.getElementById('contenedorPermisos').style.display = 'block';
  document.getElementById('rolSeleccionado').textContent = rolNombre;

  fetch(`/api/permisos/${rolId}`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('tblPermisos');
      tbody.innerHTML = data.map(mod => `
        <tr>
          <td>${mod.nombre}</td>
          ${['ver','crear','editar','eliminar'].map(a => `
            <td><input type="checkbox" data-mod="${mod.id}" data-acc="${a}" ${mod[a] ? 'checked' : ''}></td>`).join('')}
        </tr>`).join('');
    });
}

// ==== MÓDULOS ====
function cargarModulos() {
  fetch('/api/modulos')
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('tblModulos');
      tbody.innerHTML = data.map(m => `
        <tr>
          <td>${m.nombre}</td>
          <td>${m.descripcion || ''}</td>
          <td><span class="badge ${m.activo ? 'text-bg-success' : 'text-bg-secondary'}">
            ${m.activo ? 'Activo' : 'Inactivo'}</span></td>
        </tr>`).join('');
    });
}

// ==== ACCIONES ====
function cargarAcciones() {
  fetch('/api/acciones')
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('tblAcciones');
      tbody.innerHTML = data.map(a => `
        <tr>
          <td>${a.nombre}</td>
          <td>${a.etiqueta}</td>
          <td><span class="badge ${a.activo ? 'text-bg-success' : 'text-bg-secondary'}">
            ${a.activo ? 'Activa' : 'Inactiva'}</span></td>
        </tr>`).join('');
    });
}
