document.addEventListener("DOMContentLoaded", () => {

  const btn = document.getElementById("btnSync");

  if (!btn) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.innerText = "Sincronizando...";

    try {
      const res = await fetch("/gastos/sync-facturas/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });

      const data = await res.json();

      if (data.ok) {
        alert("✔ Sincronización exitosa");
        location.reload();
      } else {
        alert("❌ Error: " + data.error);
      }

    } catch (e) {
      alert("Error inesperado");
    } finally {
      btn.disabled = false;
      btn.innerText = "🔄 Sincronizar ahora";
    }
  });

});

function getCookie(name) {
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
}