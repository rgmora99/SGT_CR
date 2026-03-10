(function () {
  const hasSwal = typeof window.Swal !== 'undefined';

  function alerta(icon, text) {
    if (!hasSwal) return;
    Swal.fire({ icon, text, confirmButtonText: 'Entendido' });
  }

  const errores = document.querySelectorAll('.text-danger.small');
  if (errores.length) {
    alerta('error', 'Hay campos con errores o datos duplicados. Revísalos antes de guardar.');
  }

  const form = document.querySelector('form[method="post"]');
  if (form) {
    form.addEventListener('submit', function (e) {
      const required = form.querySelectorAll('[required]');
      for (const field of required) {
        if (!field.value || !String(field.value).trim()) {
          e.preventDefault();
          field.focus();
          alerta('warning', 'Completa todos los campos obligatorios.');
          return;
        }
      }
    });
  }
})();
