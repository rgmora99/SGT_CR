// ================================
// CIAN - Login Gestor de Contratos
// ================================

// Mostrar/ocultar contraseña
document.addEventListener("DOMContentLoaded", () => {
  const togglePassword = document.getElementById("togglePassword");
  const passwordInput = document.getElementById("clave");

  togglePassword.addEventListener("click", () => {
    const isHidden = passwordInput.type === "password";
    passwordInput.type = isHidden ? "text" : "password";
    togglePassword.innerHTML = isHidden
      ? '<i class="fa-solid fa-eye"></i>'
      : '<i class="fa-solid fa-eye-slash"></i>';
  });

  // Spinner al enviar el formulario
  const loginBtn = document.getElementById("loginBtn");
  loginBtn.addEventListener("click", () => {
    const text = document.getElementById("loginText");
    const spinner = document.getElementById("spinner");
    text.textContent = "Verificando...";
    spinner.classList.remove("d-none");
  });
});
