(function () {
  const hasSwal = typeof window.Swal !== 'undefined';

  const toIcon = (level) => {
    const normalized = String(level || '').toLowerCase();
    if (normalized.includes('error')) return 'error';
    if (normalized.includes('warning')) return 'warning';
    if (normalized.includes('success')) return 'success';
    return 'info';
  };

  const showMessages = async () => {
    const messages = Array.isArray(window.GASTOS_MESSAGES) ? window.GASTOS_MESSAGES.filter(m => m && m.text) : [];
    if (!messages.length) return;

    if (!hasSwal) {
      window.alert(messages.map((m) => `• ${m.text}`).join('\n'));
      return;
    }

    const priority = { error: 4, warning: 3, success: 2, info: 1 };
    const icon = messages
      .map((m) => toIcon(m.level))
      .sort((a, b) => (priority[b] || 0) - (priority[a] || 0))[0] || 'info';

    await Swal.fire({
      icon,
      title: messages.length > 1 ? 'Validaciones del formulario' : 'Mensaje',
      html: `<ul style="text-align:left; padding-left:1rem; margin:0;">${messages.map((m) => `<li>${m.text}</li>`).join('')}</ul>`,
      confirmButtonText: 'Aceptar',
    });
  };

  const bindAnularConfirmation = () => {
    document.querySelectorAll('.js-anular-form').forEach((form) => {
      form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const proveedor = form.dataset.proveedor || 'este proveedor';
        const factura = form.dataset.factura || 'N/A';

        if (!hasSwal) {
          if (window.confirm(`¿Anular gasto de ${proveedor} (Factura: ${factura})?`)) {
            form.submit();
          }
          return;
        }

        const result = await Swal.fire({
          title: '¿Anular gasto?',
          html: `Se anulará el gasto de <strong>${proveedor}</strong><br>Factura: <strong>${factura}</strong>`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Sí, anular',
          cancelButtonText: 'Cancelar',
          reverseButtons: true,
          focusCancel: true,
        });

        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  };

  const bindFilterValidation = () => {
    const form = document.getElementById('filtrosGastosForm');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
      const fechaDesde = (form.querySelector('#fecha_desde')?.value || '').trim();
      const fechaHasta = (form.querySelector('#fecha_hasta')?.value || '').trim();

      if (!fechaDesde || !fechaHasta || fechaDesde <= fechaHasta) {
        return;
      }

      event.preventDefault();
      const text = "La fecha 'Desde' no puede ser mayor que la fecha 'Hasta'.";

      if (!hasSwal) {
        window.alert(text);
        return;
      }

      await Swal.fire({
        icon: 'warning',
        title: 'Rango de fechas inválido',
        text,
        confirmButtonText: 'Entendido',
      });
    });
  };

  showMessages();
  bindAnularConfirmation();
  bindFilterValidation();
})();
