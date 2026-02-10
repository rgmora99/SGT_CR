document.addEventListener("DOMContentLoaded", () => {

  /* ============================
     REFERENCIAS PRINCIPALES
  ============================ */
  const sidebar   = document.getElementById("sidebar");
  const main      = document.getElementById("mainContent");
  const toggleBtn = document.getElementById("btnToggleTop");
  const backdrop  = document.getElementById("sidebarBackdrop");

  const submenuLinks = document.querySelectorAll(".toggle-submenu");

  /* ============================
     UTILIDADES
  ============================ */
  const isMobile = () => window.innerWidth < 992;

  /* ============================
     SIDEBAR OPEN / CLOSE
  ============================ */
  function openMenu() {
    sidebar.classList.add("active");
    document.body.classList.add("menu-open");
  }

  function closeMenu() {
    sidebar.classList.remove("active");
    document.body.classList.remove("menu-open");
  }

  function toggleSidebar() {
    if (isMobile()) {
      sidebar.classList.contains("active") ? closeMenu() : openMenu();
    } else {
      sidebar.classList.toggle("collapsed");
      main.classList.toggle("collapsed");
    }
  }

  toggleBtn.addEventListener("click", toggleSidebar);
  backdrop.addEventListener("click", closeMenu);

  /* ============================
     SUBMENÚS
  ============================ */
  submenuLinks.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();

      const parent = link.closest(".has-submenu");

      // cerrar otros submenús (acordeón)
      document.querySelectorAll(".has-submenu.open").forEach(item => {
        if (item !== parent) {
          item.classList.remove("open");
        }
      });

      parent.classList.toggle("open");
    });
  });

  /* ============================
     AUTO-CERRAR EN MOBILE
  ============================ */
  window.addEventListener("resize", () => {
    if (!isMobile()) {
      closeMenu();
    }
  });

});
