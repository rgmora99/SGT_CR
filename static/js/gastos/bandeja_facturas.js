document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".bandeja-page");
  const btnSync = document.getElementById("btnSync");
  const btnReloadMeta = document.getElementById("btnReloadMeta");
  const feedback = document.getElementById("syncFeedback");
  const autoSyncToggle = document.getElementById("autoSyncToggle");
  const filterForm = document.querySelector('form[aria-label="Filtros de facturas"]');
  const rejectForms = document.querySelectorAll(".reject-form");

  if (!page || !btnSync || !feedback || !autoSyncToggle) return;

  const SYNC_INTERVAL_MS = 2 * 60 * 1000;
  const STORAGE_KEY = "bandeja_auto_sync_enabled";
  const syncUrl = page.dataset.syncUrl;
  const reloadUrl = page.dataset.reloadUrl;
  let isSyncing = false;
  let intervalId = null;

  const hasSwal = typeof Swal !== "undefined" && typeof Swal.fire === "function";

  const showToast = (icon, title) => {
    if (window.SwalToast && typeof window.SwalToast.fire === "function") {
      window.SwalToast.fire({ icon, title });
      return;
    }
    if (hasSwal) {
      Swal.fire({ icon, title, toast: true, position: "top-end", timer: 2200, showConfirmButton: false });
      return;
    }
    console.log(`${icon.toUpperCase()}: ${title}`);
  };

  const showModal = ({ icon = "info", title = "Información", text = "", confirmButtonText = "Entendido" }) => {
    if (hasSwal) {
      return Swal.fire({
        icon,
        title,
        text,
        confirmButtonText,
        customClass: { confirmButton: "btn btn-primary" },
        buttonsStyling: false,
      });
    }
    alert(`${title}\n\n${text}`.trim());
    return Promise.resolve({ isConfirmed: true });
  };

  const parseServerMessages = () => {
    const node = document.getElementById("django-messages-json");
    if (!node) return [];
    try {
      return JSON.parse(node.textContent || "[]");
    } catch {
      return [];
    }
  };

  const showServerMessages = () => {
    const messages = parseServerMessages();
    if (!messages.length) return;

    messages.forEach((message, index) => {
      const tag = String(message.tags || "").toLowerCase();
      let icon = "info";
      if (tag.includes("error")) icon = "error";
      else if (tag.includes("warning")) icon = "warning";
      else if (tag.includes("success")) icon = "success";

      window.setTimeout(() => showToast(icon, message.text || ""), index * 120);
    });
  };

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
    if (isSyncing || (btnSync.disabled && !silent)) {
      if (!silent && !isSyncing && btnSync.disabled) {
        await showModal({
          icon: "warning",
          title: "Sin conexiones activas",
          text: "Configura al menos un correo activo antes de sincronizar facturas.",
        });
      }
      return;
    }

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
        const errorMsg = data.error || "No se pudo sincronizar.";
        if (!silent) {
          showFeedback(errorMsg, "error");
        }
        if (data.code === "sync_in_progress") {
          showToast("info", "Ya hay una sincronización en proceso para este negocio.");
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
        if (!silent) showToast("success", `Se agregaron ${total} factura(s) nuevas.`);
        setTimeout(() => window.location.reload(), 900);
        return;
      }

      if (!silent) {
        const summary = `Sin nuevas. Procesados: ${procesados}, duplicadas: ${duplicadas}, sin XML: ${sinXml}, XML inválidos: ${xmlInvalidos}, errores: ${errores}.`;
        showFeedback(summary, errores > 0 ? "error" : "info");
        showToast(errores > 0 ? "warning" : "info", summary);
      }
    } catch (error) {
      if (!silent) {
        showFeedback("Error inesperado durante la sincronización.", "error");
        showToast("error", "Error inesperado durante la sincronización.");
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
        showToast("error", data.error || "No se pudo recalcular metadata.");
        return;
      }

      const msg = `Recálculo completado. Actualizadas: ${data.actualizadas}, sin XML: ${data.sin_xml}, errores: ${data.errores}.`;
      showFeedback(msg, data.errores > 0 ? "info" : "success");
      showToast(data.errores > 0 ? "warning" : "success", msg);

      setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
      showFeedback("Error inesperado durante recálculo.", "error");
      showToast("error", "Error inesperado durante recálculo.");
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

  const setupFilterValidation = () => {
    if (!filterForm) return;
    const qInput = filterForm.querySelector("#id_q");

    filterForm.addEventListener("submit", async (event) => {
      const q = (qInput?.value || "").trim();
      if (q && q.length < 2) {
        event.preventDefault();
        await showModal({
          icon: "warning",
          title: "Texto muy corto",
          text: "Para buscar por texto, ingresa al menos 2 caracteres.",
        });
        qInput?.focus();
      }
    });
  };

  const setupRejectConfirmation = () => {
    rejectForms.forEach((form) => {
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const proveedor = form.dataset.proveedor || "Proveedor desconocido";
        const numero = form.dataset.factura || "Sin número";

        const result = hasSwal
          ? await Swal.fire({
              icon: "warning",
              title: "¿Rechazar factura?",
              html: `<div class="text-start small">` +
                `<div><strong>Proveedor:</strong> ${proveedor}</div>` +
                `<div><strong>Factura:</strong> ${numero}</div>` +
                `<div class="mt-2">Esta acción cambiará el estado a <strong>rechazada</strong>.</div>` +
                `</div>`,
              showCancelButton: true,
              confirmButtonText: "Sí, rechazar",
              cancelButtonText: "Cancelar",
              reverseButtons: true,
              customClass: {
                confirmButton: "btn btn-danger me-2",
                cancelButton: "btn btn-outline-secondary",
              },
              buttonsStyling: false,
            })
          : { isConfirmed: confirm("¿Deseas rechazar esta factura?") };

        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  };

  showServerMessages();
  setupFilterValidation();
  setupRejectConfirmation();

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
    showToast("info", autoSyncToggle.checked ? "Auto-sync activado." : "Auto-sync desactivado.");
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
