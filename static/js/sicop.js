document.addEventListener("DOMContentLoaded", () => {
  const btnSync = document.getElementById("btnSincronizar");
  const estadoConexion = document.getElementById("estadoConexion");
  const lblUltimaSync = document.getElementById("lblUltimaSync");

  btnSync.addEventListener("click", async () => {
    btnSync.disabled = true;
    btnSync.innerHTML = '<i class="bi bi-arrow-repeat spin me-1"></i> Sincronizando...';

    // Simulación de proceso
    setTimeout(() => {
      lblUltimaSync.textContent = new Date().toLocaleString();
      estadoConexion.innerHTML = '<i class="bi bi-check-circle me-1"></i> Conectado';
      estadoConexion.classList.replace("text-bg-danger", "text-bg-success");
      btnSync.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Sincronizar ahora';
      btnSync.disabled = false;

      alert("Sincronización completada con éxito.");
    }, 2500);
  });
});
