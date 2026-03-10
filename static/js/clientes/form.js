(function () {
  const form = document.querySelector('.form-cliente form');
  if (!form) return;

  const hasSwal = typeof window.Swal !== 'undefined' && typeof window.Swal.fire === 'function';
  const identificacionInput = form.querySelector('[name="identificacion"]');
  const tipoInput = form.querySelector('[name="tipo_identificacion"]');
  const submitBtn = form.querySelector('button[type="submit"]');
  const modo = window.CLIENTE_MODO === 'editar' ? 'editar' : 'crear';

  const parseErrors = () => {
    const node = document.getElementById('cliente-form-errors');
    if (!node) return {};
    try {
      return JSON.parse(node.textContent || '{}');
    } catch {
      return {};
    }
  };

  const formatFieldName = (field) =>
    String(field || '')
      .replaceAll('_', ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());

  const showValidationModal = (errors) => {
    const entries = Object.entries(errors || {}).filter(([, msgs]) => Array.isArray(msgs) && msgs.length);
    if (!entries.length || !hasSwal) return;

    const html = `<ul style="text-align:left; padding-left:1rem; margin:0;">${entries
      .map(([field, msgs]) => `<li><strong>${formatFieldName(field)}</strong>: ${msgs.join(', ')}</li>`)
      .join('')}</ul>`;

    Swal.fire({
      icon: 'error',
      title: 'Revisa el formulario',
      html,
      confirmButtonText: 'Entendido',
    });
  };

  const markInvalid = (input, invalid, msg = '') => {
    if (!input) return;
    input.classList.toggle('is-invalid', invalid);
    input.setCustomValidity(invalid ? msg : '');
  };

  const validarDuplicadoCedula = async ({ showAlert = false } = {}) => {
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
        if (hasSwal && showAlert) {
          await Swal.fire({
            icon: 'warning',
            title: 'Identificación duplicada',
            text: msg,
            confirmButtonText: 'Entendido',
          });
        }
        return false;
      }

      markInvalid(identificacionInput, false);
      return true;
    } catch {
      return true;
    }
  };

  const confirmarGuardado = async () => {
    if (!hasSwal) return true;

    const res = await Swal.fire({
      icon: 'question',
      title: modo === 'editar' ? 'Guardar cambios del cliente' : 'Registrar nuevo cliente',
      text: modo === 'editar'
        ? '¿Desea actualizar la información del cliente?'
        : '¿Desea guardar este nuevo cliente?',
      showCancelButton: true,
      confirmButtonText: modo === 'editar' ? 'Sí, actualizar' : 'Sí, guardar',
      cancelButtonText: 'Cancelar',
      reverseButtons: true,
    });

    return !!res.isConfirmed;
  };

  identificacionInput?.addEventListener('blur', () => {
    void validarDuplicadoCedula({ showAlert: true });
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
        await Swal.fire({
          icon: 'warning',
          title: 'Tipo requerido',
          text: 'Seleccione un tipo de identificación.',
          confirmButtonText: 'Entendido',
        });
      }
      return;
    }

    const okDuplicado = await validarDuplicadoCedula({ showAlert: true });
    if (!okDuplicado) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    const confirmado = await confirmarGuardado();
    if (!confirmado) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    if (hasSwal) {
      submitBtn?.setAttribute('disabled', 'disabled');
      Swal.fire({
        title: modo === 'editar' ? 'Actualizando cliente...' : 'Guardando cliente...',
        allowEscapeKey: false,
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading(),
      });
    }
  });

  showValidationModal(parseErrors());
})();
