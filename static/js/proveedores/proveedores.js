/* =========================================================
   CIAN CCR — Lógica para el módulo "Proveedores"
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const buscarInput = document.getElementById("txtBuscar");
  const selCategoria = document.getElementById("selCategoria");
  const selEstado = document.getElementById("selEstado");
  const fDesde = document.getElementById("fDesde");
  const fHasta = document.getElementById("fHasta");
  const btnFiltrar = document.getElementById("btnFiltrar");
  const btnLimpiar = document.getElementById("btnLimpiar");
  const chkAll = document.getElementById("chkAll");
  const filas = document.querySelectorAll("#tblProveedores tr");

  // === FILTRO BÁSICO ===
  btnFiltrar.addEventListener("click", () => {
    const busqueda = buscarInput.value.toLowerCase();
    const categoria = selCategoria.value;
    const estado = selEstado.value;

    filas.forEach(row => {
      const texto = row.innerText.toLowerCase();
      const matchBusqueda = texto.includes(busqueda);
      const matchCategoria = !categoria || texto.includes(categoria.toLowerCase());
      const matchEstado = !estado || texto.includes(estado.toLowerCase());

      if (matchBusqueda && matchCategoria && matchEstado) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  });

  // === LIMPIAR FILTROS ===
  btnLimpiar.addEventListener("click", () => {
    buscarInput.value = "";
    selCategoria.value = "";
    selEstado.value = "";
    fDesde.value = "";
    fHasta.value = "";
    filas.forEach(row => row.style.display = "");
  });

  // === CHECKBOX GENERAL ===
  chkAll.addEventListener("change", (e) => {
    document.querySelectorAll(".chkRow").forEach(chk => {
      chk.checked = e.target.checked;
    });
  });

  // === ACCIONES DE BOTONES ===
  document.querySelectorAll(".action-btn.view").forEach(btn => {
    btn.addEventListener("click", () => {
      alert("👁️ Visualización de proveedor — aquí se abrirá el detalle del registro.");
    });
  });

  document.querySelectorAll(".action-btn.edit").forEach(btn => {
    btn.addEventListener("click", () => {
      alert("✏️ Edición de proveedor — se redirigirá al formulario de edición.");
    });
  });

  document.querySelectorAll(".action-btn.danger").forEach(btn => {
    btn.addEventListener("click", () => {
      if (confirm("¿Seguro que desea eliminar este proveedor?")) {
        btn.closest("tr").remove();
      }
    });
  });
});
