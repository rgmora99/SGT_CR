(function () {
  const form = document.querySelector('.form-cliente form');
  if (!form) return;

  const hasSwal = typeof window.Swal !== 'undefined' && typeof window.Swal.fire === 'function';
  const identificacionInput = form.querySelector('[name="identificacion"]');
  const tipoInput = form.querySelector('[name="tipo_identificacion"]');

  const parseErrors = () => {
    const node = document.getElementById('cliente-form-errors');
    if (!node) return {};
    try {
      return JSON.parse(node.textContent || '{}');
    } catch {
      return {};
    }
  };

  const showValidationModal = (errors) => {
    const entries = Object.entries(errors || {}).filter(([, msgs]) => Array.isArray(msgs) && msgs.length);
    if (!entries.length) return;
    const html = `<ul style="text-align:left; padding-left:1rem; margin:0;">${entries
      .map(([field, msgs]) => `<li><strong>${field}</strong>: ${msgs.join(', ')}</li>`)
      .join('')}</ul>`;

    if (hasSwal) {
      Swal.fire({ icon: 'error', title: 'Revisa el formulario', html, confirmButtonText: 'Entendido' });
    }
  };

  const markInvalid = (input, invalid, msg = '') => {
    if (!input) return;
    input.classList.toggle('is-invalid', invalid);
    input.setCustomValidity(invalid ? msg : '');
  };

  const validarDuplicadoCedula = async () => {
    if (!identificacionInput || !window.CLIENTES_VALIDAR_IDENTIFICACION_URL) return true;
    const identificacion = (identificacionInput.value || '').trim();
    if (!identificacion) return true;

    const params = new URLSearchParams({ identificacion });
    if (window.CLIENTE_ID) params.append('cliente_id', window.CLIENTE_ID);

    try {
      const res = await fetch(`${window.CLIENTES_VALIDAR_IDENTIFICACION_URL}?${params.toString()}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      if (!res.ok) return true;
      const data = await res.json();
      if (data.duplicado) {
        const msg = 'La identificación ya está registrada. No se permiten duplicados.';
        markInvalid(identificacionInput, true, msg);
        if (hasSwal) {
          await Swal.fire({ icon: 'warning', title: 'Identificación duplicada', text: msg, confirmButtonText: 'Entendido' });
        }
        return false;
      }
      markInvalid(identificacionInput, false);
      return true;
    } catch {
      return true;
    }
  };

  identificacionInput?.addEventListener('blur', () => {
    void validarDuplicadoCedula();
  });

  form.addEventListener('submit', async (event) => {
    const errors = parseErrors();
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
      showValidationModal(errors);
      return;
    }

    if (!tipoInput?.value) {
      event.preventDefault();
      if (hasSwal) {
        await Swal.fire({ icon: 'warning', title: 'Tipo requerido', text: 'Seleccione un tipo de identificación.' });
      }
      return;
    }

    const okDuplicado = await validarDuplicadoCedula();
    if (!okDuplicado) {
      event.preventDefault();
      event.stopPropagation();
    }
  });

  showValidationModal(parseErrors());
})();
