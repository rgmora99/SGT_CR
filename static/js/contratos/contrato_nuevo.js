document.addEventListener("DOMContentLoaded", () => {
  const panels = document.querySelectorAll(".wizard-panel");
  const steps = document.querySelectorAll(".wizard-step");

  let current = 1;

  function show(step) {
    panels.forEach(p => {
      p.classList.toggle("active", p.dataset.step == step);
    });

    steps.forEach(s => {
      s.classList.toggle("active", s.dataset.step <= step);
    });

    current = step;
  }

  document.querySelectorAll(".next").forEach(btn => {
    btn.addEventListener("click", () => {
      if (current < panels.length) show(current + 1);
    });
  });

  document.querySelectorAll(".prev").forEach(btn => {
    btn.addEventListener("click", () => {
      if (current > 1) show(current - 1);
    });
  });

  show(current);
});
