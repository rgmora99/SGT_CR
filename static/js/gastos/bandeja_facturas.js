document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".bandeja-page");
  const btnSync = document.getElementById("btnSync");
  const btnReloadMeta = document.getElementById("btnReloadMeta");
  const feedback = document.getElementById("syncFeedback");
  const autoSyncToggle = document.getElementById("autoSyncToggle");

  if (!page || !btnSync || !feedback || !autoSyncToggle) return;

  const SYNC_INTERVAL_MS = 2 * 60 * 1000;
  const STORAGE_KEY = "bandeja_auto_sync_enabled";
  const syncUrl = page.dataset.syncUrl;
  const reloadUrl = page.dataset.reloadUrl;
  let isSyncing = false;
  let intervalId = null;

  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  const showFeedback = (message, type = "info") => {
    feedback.className = `sync-feedback ${type}`;
    feedback.textContent = message;
    feedback.classList.remove("d-none");
  };

  const setButtonState = (syncing) => {
    btnSync.disabled = syncing;
    if (btnReloadMeta) btnReloadMeta.disabled = syncing;
    btnSync.innerText = syncing ? "Sincronizando..." : "⟳ Sync";
  };

  const syncFacturas = async ({ silent = false } = {}) => {
    if (isSyncing || (btnSync.disabled && !silent)) return;

    isSyncing = true;
    setButtonState(true);

    if (!silent) {
      showFeedback("Sincronizando facturas...", "info");
    }

    try {
      const res = await fetch(syncUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        if (!silent) {
          showFeedback(data.error || "No se pudo sincronizar.", "error");
        }
        return;
      }

      const total = Number(data.facturas_creadas || 0);
      const duplicadas = Number(data.facturas_duplicadas || 0);
      const sinXml = Number(data.correos_sin_xml || 0);
      const xmlInvalidos = Number(data.xml_invalidos || 0);
      const errores = Number(data.errores || 0);
      const procesados = Number(data.correos_procesados || 0);

      if (total > 0) {
        showFeedback(
          `✔ ${total} nuevas. Procesados: ${procesados}. Duplicadas: ${duplicadas}.`,
          "success"
        );
        setTimeout(() => window.location.reload(), 900);
        return;
      }

      if (!silent) {
        showFeedback(
          `Sin nuevas. Procesados: ${procesados}, duplicadas: ${duplicadas}, sin XML: ${sinXml}, XML inválidos: ${xmlInvalidos}, errores: ${errores}.`,
          errores > 0 ? "error" : "info"
        );
      }
    } catch (error) {
      if (!silent) {
        showFeedback("Error inesperado durante la sincronización.", "error");
      }
    } finally {
      isSyncing = false;
      setButtonState(false);
    }
  };

  const recargarMetadata = async () => {
    if (!reloadUrl || isSyncing) return;

    isSyncing = true;
    setButtonState(true);
    showFeedback("Recalculando moneda y alertas desde XML guardado...", "info");

    try {
      const res = await fetch(reloadUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        showFeedback(data.error || "No se pudo recalcular metadata.", "error");
        return;
      }

      showFeedback(
        `Recálculo completado. Actualizadas: ${data.actualizadas}, sin XML: ${data.sin_xml}, errores: ${data.errores}.`,
        data.errores > 0 ? "info" : "success"
      );

      setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
      showFeedback("Error inesperado durante recálculo.", "error");
    } finally {
      isSyncing = false;
      setButtonState(false);
    }
  };

  const startAutoSync = () => {
    if (intervalId) window.clearInterval(intervalId);

    intervalId = window.setInterval(() => {
      if (document.visibilityState === "visible" && autoSyncToggle.checked) {
        syncFacturas({ silent: true });
      }
    }, SYNC_INTERVAL_MS);
  };

  const initialAutoSync = localStorage.getItem(STORAGE_KEY);
  autoSyncToggle.checked = initialAutoSync !== "0";

  autoSyncToggle.addEventListener("change", () => {
    localStorage.setItem(STORAGE_KEY, autoSyncToggle.checked ? "1" : "0");
    showFeedback(
      autoSyncToggle.checked
        ? "Sincronización automática activada."
        : "Sincronización automática desactivada.",
      "info"
    );
  });

  btnSync.addEventListener("click", () => syncFacturas({ silent: false }));
  if (btnReloadMeta) btnReloadMeta.addEventListener("click", recargarMetadata);

  if (!btnSync.disabled) {
    syncFacturas({ silent: true });
    startAutoSync();
  } else {
    showFeedback("Configura al menos un correo activo para habilitar sincronización.", "info");
  }
});
