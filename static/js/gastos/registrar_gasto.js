(function () {
  const form = document.querySelector('.registrar-card form');
  if (!form) return;

  const categoria = form.querySelector('[name="categoria"]');
  const fechaGasto = form.querySelector('[name="fecha_gasto"]');
  const tipoCambio = form.querySelector('[name="tipo_cambio"]');

  const monedasDistintas = (form.dataset.monedasDistintas || '0') === '1';

  const showAlert = ({ icon = 'info', title = 'Información', text = '' }) => {
    if (typeof Swal !== 'undefined' && Swal.fire) {
      return Swal.fire({
        icon,
        title,
        text,
        confirmButtonText: 'Entendido',
        customClass: { confirmButton: 'btn btn-primary' },
        buttonsStyling: false,
      });
    }
    alert(`${title}\n\n${text}`.trim());
    return Promise.resolve();
  };

  const markInvalid = (field, invalid = true) => {
    if (!field) return;
    field.classList.toggle('is-invalid', invalid);
  };

  const parseServerMessages = () => {
    const node = document.getElementById('django-messages-json');
    if (!node) return [];
    try {
      return JSON.parse(node.textContent || '[]');
    } catch {
      return [];
    }
  };

  const showServerMessages = () => {
    const messages = parseServerMessages();
    if (!messages.length) return;

    messages.forEach((message, index) => {
      const tag = String(message.tags || '').toLowerCase();
      let icon = 'info';
      let title = 'Información';

      if (tag.includes('error')) {
        icon = 'error';
        title = 'Validación';
      } else if (tag.includes('warning')) {
        icon = 'warning';
        title = 'Atención';
      } else if (tag.includes('success')) {
        icon = 'success';
        title = 'Correcto';
      }

      setTimeout(() => {
        showAlert({ icon, title, text: message.text || '' });
      }, index * 120);
    });
  };

  showServerMessages();

  [categoria, fechaGasto, tipoCambio].forEach((field) => {
    if (!field) return;
    field.addEventListener('input', () => markInvalid(field, false));
    field.addEventListener('change', () => markInvalid(field, false));
  });

  form.addEventListener('submit', async (event) => {
    const categoriaVal = (categoria?.value || '').trim();
    const fechaVal = (fechaGasto?.value || '').trim();
    const tipoCambioVal = (tipoCambio?.value || '').trim();

    if (!categoriaVal) {
      event.preventDefault();
      markInvalid(categoria, true);
      await showAlert({
        icon: 'warning',
        title: 'Falta categoría',
        text: 'Debes seleccionar una categoría para registrar el gasto.',
      });
      categoria?.focus();
      return;
    }

    if (!fechaVal) {
      event.preventDefault();
      markInvalid(fechaGasto, true);
      await showAlert({
        icon: 'warning',
        title: 'Falta fecha del gasto',
        text: 'Indica la fecha del gasto para continuar.',
      });
      fechaGasto?.focus();
      return;
    }

    if (monedasDistintas) {
      const tc = Number(tipoCambioVal);
      if (!tipoCambioVal || Number.isNaN(tc) || tc <= 0) {
        event.preventDefault();
        markInvalid(tipoCambio, true);
        await showAlert({
          icon: 'error',
          title: 'Tipo de cambio inválido',
          text: 'La factura está en una moneda distinta a la base del negocio. Ingresa un tipo de cambio mayor que cero.',
        });
        tipoCambio?.focus();
      }
    }
  });
})();
