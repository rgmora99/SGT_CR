(function () {
  const hasSwal = typeof window.Swal !== 'undefined';
  const form = document.getElementById('editarGastoForm');
  if (!form) return;

  const meta = window.GASTO_EDITAR_META || {};
  const monedaFactura = String(meta.monedaFactura || '').toUpperCase();
  const monedaBase = String(meta.monedaBase || '').toUpperCase();

  const toIcon = (level) => {
    const normalized = String(level || '').toLowerCase();
    if (normalized.includes('error')) return 'error';
    if (normalized.includes('warning')) return 'warning';
    if (normalized.includes('success')) return 'success';
    return 'info';
  };

  const showMessages = async () => {
    const messages = Array.isArray(window.GASTOS_MESSAGES)
      ? window.GASTOS_MESSAGES.filter((m) => m && m.text)
      : [];
    if (!messages.length) return;

    const html = `<ul style="text-align:left; padding-left:1rem; margin:0;">${messages.map((m) => `<li>${m.text}</li>`).join('')}</ul>`;

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
      html,
      confirmButtonText: 'Aceptar',
    });
  };

  form.addEventListener('submit', async (event) => {
    const categoria = (form.querySelector('[name="categoria"]')?.value || '').trim();
    const fecha = (form.querySelector('[name="fecha_gasto"]')?.value || '').trim();
    const tipoCambioInput = (form.querySelector('[name="tipo_cambio"]')?.value || '').trim();

    let error = '';

    if (!categoria) {
      error = 'Debes seleccionar una categoría.';
    } else if (!fecha) {
      error = 'Debes indicar la fecha del gasto.';
    } else if (monedaFactura && monedaBase && monedaFactura !== monedaBase) {
      const val = Number(tipoCambioInput);
      if (!tipoCambioInput || Number.isNaN(val) || val <= 0) {
        error = `Debes indicar un tipo de cambio válido (> 0) para convertir de ${monedaFactura} a ${monedaBase}.`;
      }
    }

    if (!error) return;

    event.preventDefault();
    if (!hasSwal) {
      window.alert(error);
      return;
    }

    await Swal.fire({
      icon: 'warning',
      title: 'Revisa el formulario',
      text: error,
      confirmButtonText: 'Entendido',
    });
  });

  showMessages();
})();
