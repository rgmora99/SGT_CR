document.addEventListener("DOMContentLoaded", () => {
  let currentStep = 1;
  const totalSteps = 3;

  const showStep = (step) => {
    document.querySelectorAll(".step-content").forEach(el => {
      el.classList.remove("active");
    });

    document.querySelector(`#step-${step}`).classList.add("active");

    document.querySelectorAll(".wizard-step").forEach(el => {
      el.classList.remove("active", "completed");
      const stepNum = parseInt(el.dataset.step);
      if (stepNum < step) el.classList.add("completed");
      if (stepNum === step) el.classList.add("active");
    });
  };

  document.querySelectorAll(".next-step").forEach(btn => {
    btn.addEventListener("click", () => {
      if (currentStep < totalSteps) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  document.querySelectorAll(".prev-step").forEach(btn => {
    btn.addEventListener("click", () => {
      if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  showStep(currentStep);
});
