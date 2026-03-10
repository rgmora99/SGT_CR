(function () {
  const toIcon = (level) => {
    const normalized = String(level || '').toLowerCase();
    if (normalized.includes('success')) return 'success';
    if (normalized.includes('error')) return 'error';
    if (normalized.includes('warning')) return 'warning';
    return 'info';
  };

  const messages = Array.isArray(window.GASTOS_MESSAGES) ? window.GASTOS_MESSAGES : [];
  messages.forEach((msg) => {
    if (!msg || !msg.text) return;
    Swal.fire({
      icon: toIcon(msg.level),
      title: msg.text,
      confirmButtonText: 'Aceptar',
    });
  });

  document.querySelectorAll('.js-anular-form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();

      const proveedor = form.dataset.proveedor || 'este proveedor';
      const factura = form.dataset.factura || 'N/A';

      const result = await Swal.fire({
        title: '¿Anular gasto?',
        html: `Se anulará el gasto de <strong>${proveedor}</strong><br>Factura: <strong>${factura}</strong>`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, anular',
        cancelButtonText: 'Cancelar',
        reverseButtons: true,
      });

      if (result.isConfirmed) {
        form.submit();
      }
    });
  });
})();
