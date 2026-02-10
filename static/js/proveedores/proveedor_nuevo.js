document.addEventListener("DOMContentLoaded", () => {
  // ===== Referencias principales =====
  const steps = document.querySelectorAll(".step-content");
  const nextBtns = document.querySelectorAll(".next-step");
  const prevBtns = document.querySelectorAll(".prev-step");
  const wizardSteps = document.querySelectorAll(".wizard-step");
  const wizardLabels = document.querySelectorAll(".wizard-labels span");
  const tipoSelect = document.getElementById("tipo");
  const form = document.getElementById("formCatalogo");

  let currentStep = 0;

  // ===== Mostrar paso actual =====
  function showStep(index) {
    steps.forEach((step, i) => {
      step.classList.toggle("active", i === index);
      wizardSteps[i].classList.toggle("active", i <= index);
      wizardLabels[i].classList.toggle("active", i === index);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // ===== Validación simple =====
  function validarPaso(stepIndex) {
    const currentForm = steps[stepIndex].querySelectorAll("input[required], select[required]");
    for (let input of currentForm) {
      if (!input.value.trim()) {
        input.classList.add("is-invalid");
        input.focus();
        return false;
      } else {
        input.classList.remove("is-invalid");
      }
    }
    return true;
  }

  // ===== Avanzar de paso =====
  nextBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (validarPaso(currentStep)) {
        if (currentStep < steps.length - 1) {
          currentStep++;
          showStep(currentStep);
        }
      }
    });
  });

  // ===== Retroceder de paso =====
  prevBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  // ===== Ocultar/mostrar secciones según tipo =====
  tipoSelect?.addEventListener("change", () => {
    const tipo = tipoSelect.value;
    const inventarioStep = document.getElementById("step-3");
    const servicioStep = document.getElementById("step-4");

    if (tipo === "Producto") {
      inventarioStep.style.display = "";
      servicioStep.style.display = "none";
    } else if (tipo === "Servicio") {
      inventarioStep.style.display = "none";
      servicioStep.style.display = "";
    } else {
      inventarioStep.style.display = "";
      servicioStep.style.display = "";
    }
  });

  // ===== Envío del formulario =====
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    // Validación final
    if (!validarPaso(currentStep)) {
      return;
    }

    // Simulación de envío (puedes cambiar por fetch hacia tu endpoint Flask)
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    console.log("Datos a enviar:", data);

    Swal.fire({
      icon: "success",
      title: "Registro completado",
      text: "El producto o servicio se guardó correctamente.",
      confirmButtonColor: "#003057",
    });

    form.reset();
    currentStep = 0;
    showStep(0);
  });

  // ===== Inicializar =====
  showStep(0);
});
