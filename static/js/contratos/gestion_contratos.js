/* =========================================================
   CIAN CCR — JS Común para el módulo "Contratos"
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {

  // ===== Seleccionar todos los checkboxes =====
  const chkAll = document.getElementById("chkAll");
  if (chkAll) {
    chkAll.addEventListener("change", () => {
      document.querySelectorAll(".chkRow").forEach(chk => chk.checked = chkAll.checked);
    });
  }

  // ===== Botón de limpieza de filtros =====
  const btnLimpiar = document.getElementById("btnLimpiar");
  if (btnLimpiar) {
    btnLimpiar.addEventListener("click", () => {
      document.querySelectorAll(".filter-bar input, .filter-bar select").forEach(el => el.value = "");
    });
  }

  // ===== Acciones en tabla (ver, editar, eliminar) =====
  document.querySelectorAll(".action-btn").forEach(btn => {
    btn.addEventListener("click", e => {
      const tipo = e.currentTarget.classList;
      if (tipo.contains("view")) mostrarMensaje("Vista detallada del registro.");
      if (tipo.contains("edit")) mostrarMensaje("Edición de registro habilitada.");
      if (tipo.contains("danger")) mostrarConfirmacion();
    });
  });

  // ===== Botón de filtrado =====
  const btnFiltrar = document.getElementById("btnFiltrar");
  if (btnFiltrar) {
    btnFiltrar.addEventListener("click", () => {
      mostrarMensaje("Filtros aplicados correctamente.");
    });
  }

  // ===== Función de mensaje rápido =====
  function mostrarMensaje(texto) {
    const toast = document.createElement("div");
    toast.className = "position-fixed bottom-0 end-0 p-3";
    toast.innerHTML = `
      <div class="toast align-items-center text-bg-success border-0 show" role="alert">
        <div class="d-flex">
          <div class="toast-body">${texto}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }

  // ===== Confirmación antes de eliminar =====
  function mostrarConfirmacion() {
    if (confirm("¿Está seguro de eliminar este registro?")) {
      mostrarMensaje("Registro eliminado correctamente.");
    }
  }

});
