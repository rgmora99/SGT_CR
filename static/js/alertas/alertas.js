document.addEventListener("DOMContentLoaded", () => {

  const chkAll = document.getElementById("chkAll");
  const rowChecks = document.querySelectorAll(".chkRow");

  // === Seleccionar todos ===
  chkAll?.addEventListener("change", () => {
    rowChecks.forEach(chk => chk.checked = chkAll.checked);
  });

  // === Botones de acción ===
  document.querySelectorAll(".action-btn.success").forEach(btn => {
    btn.addEventListener("click", e => {
      const row = e.target.closest("tr");
      const estado = row.querySelector("td:nth-child(7) span");
      estado.className = "badge rounded-pill text-bg-success";
      estado.textContent = "Atendida";
    });
  });

  document.querySelectorAll(".action-btn.danger").forEach(btn => {
    btn.addEventListener("click", e => {
      if (confirm("¿Eliminar esta alerta?")) {
        e.target.closest("tr").remove();
      }
    });
  });

  document.getElementById("btnLimpiar")?.addEventListener("click", () => {
    document.getElementById("txtBuscar").value = "";
    document.getElementById("selTipo").selectedIndex = 0;
    document.getElementById("selEstado").selectedIndex = 0;
    document.getElementById("fDesde").value = "";
    document.getElementById("fHasta").value = "";
  });

  document.getElementById("btnFiltrar")?.addEventListener("click", () => {
    alert("Filtrado aplicado (demo). Aquí se conectará al backend o API de alertas.");
  });

});
