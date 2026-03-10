(function () {
  const hasSwal = typeof window.Swal !== 'undefined';
  const form = document.getElementById('registrarGastoForm');
  if (!form) return;

  const meta = window.GASTO_REGISTRAR_META || {};
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

    if (!hasSwal) {
      window.alert(messages.map((m) => `- ${m.text}`).join('\n'));
      return;
    }

    const priority = { error: 4, warning: 3, success: 2, info: 1 };
    const icon = messages
      .map((m) => toIcon(m.level))
      .sort((a, b) => (priority[b] || 0) - (priority[a] || 0))[0] || 'info';

    await Swal.fire({
      icon,
      title: messages.length > 1 ? 'Revisa el formulario' : 'Información',
      html: `<ul style="text-align:left; padding-left:1rem; margin:0;">${messages.map((m) => `<li>${m.text}</li>`).join('')}</ul>`,
      confirmButtonText: 'Entendido',
    });
  };

  form.addEventListener('submit', async (event) => {
    const categoria = (form.querySelector('[name="categoria"]')?.value || '').trim();
    const fecha = (form.querySelector('[name="fecha_gasto"]')?.value || '').trim();
    const metodo = (form.querySelector('[name="metodo_pago"]')?.value || '').trim();
    const referencia = (form.querySelector('[name="referencia_contable"]')?.value || '').trim();
    const tipoCambio = (form.querySelector('[name="tipo_cambio"]')?.value || '').trim();

    const allowed = new Set(['', 'EFECTIVO', 'TRANSFERENCIA', 'TARJETA']);
    let error = '';

    if (!categoria) {
      error = 'Debes seleccionar una categoría para registrar el gasto.';
    } else if (!fecha) {
      error = 'Debes indicar la fecha del gasto.';
    } else if (!allowed.has(metodo)) {
      error = 'El método de pago seleccionado no es válido.';
    } else if (referencia.length > 80) {
      error = 'La referencia contable no puede superar 80 caracteres.';
    } else if (monedaFactura && monedaBase && monedaFactura !== monedaBase) {
      const val = Number(tipoCambio);
      if (!tipoCambio || Number.isNaN(val) || val <= 0) {
        error = `Debes ingresar un tipo de cambio válido (> 0) para convertir de ${monedaFactura} a ${monedaBase}.`;
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
