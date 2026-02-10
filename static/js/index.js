document.addEventListener("DOMContentLoaded", () => {
  // Inicializa AOS (animaciones de scroll)
  AOS.init({
    duration: 800,
    easing: "ease-in-out",
    once: true,
  });

  // Efecto de clic en las tarjetas
  document.querySelectorAll(".card-menu").forEach(card => {
    card.addEventListener("click", () => {
      const title = card.querySelector("h5").textContent;
      console.log(`➡ Navegando a módulo: ${title}`);
    });
  });
});
