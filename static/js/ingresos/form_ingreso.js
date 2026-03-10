(function () {
  const addBtn = document.getElementById('add-detalle');
  const container = document.getElementById('detalles-container');
  const ingresoForm = document.getElementById('ingreso-form');
  const monedaSelect = document.getElementById('id_moneda');
  const fechaIngresoInput = document.getElementById('id_fecha_ingreso');
  const tipoCambioWrap = document.querySelector('.js-tipo-cambio-wrap');
  const tipoCambioInput = document.getElementById('id_tipo_cambio');
  const tipoCambioBtn = document.getElementById('btnTipoCambioAuto');
  const tipoCambioSource = document.getElementById('tipoCambioSource');

  const log = (...args) => console.log('[ingresos/form]', ...args);

  const getFormsetPrefix = () => {
    const totalInput = ingresoForm?.querySelector('input[name$="-TOTAL_FORMS"]');
    if (!totalInput || !totalInput.name.includes('-TOTAL_FORMS')) return null;
    return totalInput.name.replace('-TOTAL_FORMS', '');
  };

  const getTotalFormsInput = () => {
    const prefix = getFormsetPrefix();
    if (!prefix) return null;
    return document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  };

  const getTodayLocalIso = () => {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  const showAlert = (icon, text) => {
    if (window.Swal) {
      window.Swal.fire({ icon, text, confirmButtonText: 'Entendido' });
    } else {
      alert(text);
    }
  };

  const showToast = (icon, title) => {
    if (!window.Swal) return;
    window.Swal.fire({
      icon,
      title,
      toast: true,
      position: 'top-end',
      timer: 1800,
      showConfirmButton: false,
      timerProgressBar: true,
    });
  };

  const updateTipoCambioVisibility = () => {
    if (!monedaSelect || !tipoCambioWrap || !tipoCambioInput) return;
    const isUSD = monedaSelect.value === 'USD';
    tipoCambioWrap.style.display = isUSD ? '' : 'none';
    tipoCambioInput.required = isUSD;
    if (!isUSD) {
      tipoCambioInput.value = '';
      if (tipoCambioSource) tipoCambioSource.textContent = '';
    }
  };

  const addDetalleLinea = () => {
    const totalFormsInput = getTotalFormsInput();
    const prefix = getFormsetPrefix();

    if (!addBtn || !container || !totalFormsInput || !prefix) {
      log('No se pudo agregar línea: referencias faltantes', {
        addBtn: Boolean(addBtn),
        container: Boolean(container),
        totalFormsInput: Boolean(totalFormsInput),
        prefix,
      });
      showAlert('error', 'No se pudo agregar la línea. Revisa la consola para más detalle.');
      return;
    }

    const index = Number(totalFormsInput.value || 0);
    const firstRow = container.querySelector('.detalle-row');
    const firstProducto = container.querySelector('select[name$="-producto"]');
    const productOptions = firstProducto ? firstProducto.innerHTML : '<option value="">---------</option>';

    if (!firstRow) {
      log('No existe fila base de detalle para clonar estructura.');
    }

    const html = `
      <div class="detalle-row row g-2 mb-2 border-bottom pb-2">
        <div class="col-md-3"><select class="form-select js-producto" name="${prefix}-${index}-producto" id="id_${prefix}-${index}-producto">${productOptions}</select></div>
        <div class="col-md-3"><input type="text" class="form-control" name="${prefix}-${index}-descripcion" maxlength="200" placeholder="Detalle del servicio o producto" id="id_${prefix}-${index}-descripcion"></div>
        <div class="col-md-2"><input type="number" class="form-control" name="${prefix}-${index}-cantidad" step="0.01" min="0.01" placeholder="Cantidad" id="id_${prefix}-${index}-cantidad"></div>
        <div class="col-md-2"><input type="number" class="form-control" name="${prefix}-${index}-precio_unitario" step="0.01" min="0" placeholder="Precio unitario" id="id_${prefix}-${index}-precio_unitario"></div>
        <div class="col-md-1"><input type="number" class="form-control" name="${prefix}-${index}-porcentaje_iva" step="0.01" min="0" value="13" id="id_${prefix}-${index}-porcentaje_iva"></div>
        <div class="col-md-1 d-flex align-items-center"><input type="checkbox" class="form-check-input" name="${prefix}-${index}-DELETE" id="id_${prefix}-${index}-DELETE"></div>
      </div>`;

    container.insertAdjacentHTML('beforeend', html);
    totalFormsInput.value = index + 1;

    log('Línea agregada', { prefix, indexNuevo: index, totalForms: totalFormsInput.value });
    showToast('success', 'Línea agregada correctamente');
  };

  const hasAtLeastOneDetalle = () => {
    if (!container) return false;
    const rows = [...container.querySelectorAll('.detalle-row')];
    return rows.some((row) => {
      const deleted = row.querySelector('input[name$="-DELETE"]')?.checked;
      if (deleted) return false;
      const descripcion = row.querySelector('input[name$="-descripcion"]')?.value?.trim();
      const producto = row.querySelector('select[name$="-producto"]')?.value;
      const cantidad = row.querySelector('input[name$="-cantidad"]')?.value;
      const precio = row.querySelector('input[name$="-precio_unitario"]')?.value;
      return Boolean(producto || descripcion || cantidad || precio);
    });
  };

  const validateFechaIngresoHoy = () => {
    if (!fechaIngresoInput || !fechaIngresoInput.value) return true;
    const todayLocal = getTodayLocalIso();
    if (fechaIngresoInput.value !== todayLocal) {
      log('Fecha inválida', { fechaIngresada: fechaIngresoInput.value, todayLocal });
      showAlert('error', 'La fecha de ingreso debe ser la fecha actual.');
      return false;
    }
    return true;
  };

  const loadTipoCambio = async () => {
    if (!window.INGRESOS_TIPO_CAMBIO_API || !tipoCambioInput) return;
    try {
      const resp = await fetch(window.INGRESOS_TIPO_CAMBIO_API, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      const data = await resp.json();
      if (!resp.ok || !data.ok) {
        throw new Error(data.error || 'No fue posible consultar tipo de cambio.');
      }
      tipoCambioInput.value = Number(data.tipo_cambio).toFixed(4);
      if (tipoCambioSource) {
        tipoCambioSource.textContent = `Fuente: ${data.fuente}`;
      }
      log('Tipo de cambio actualizado', data);
      showToast('success', 'Tipo de cambio actualizado');
    } catch (error) {
      log('Error consultando tipo de cambio', error);
      showAlert('warning', error.message || 'No fue posible obtener tipo de cambio automático.');
    }
  };

  if (addBtn) {
    addBtn.addEventListener('click', addDetalleLinea);
  }

  if (fechaIngresoInput) {
    const todayLocal = getTodayLocalIso();
    fechaIngresoInput.min = todayLocal;
    fechaIngresoInput.max = todayLocal;
    log('Restricción fecha aplicada', { todayLocal });
  }

  if (monedaSelect) {
    monedaSelect.addEventListener('change', () => {
      updateTipoCambioVisibility();
      if (monedaSelect.value === 'USD') {
        loadTipoCambio();
      }
    });
    updateTipoCambioVisibility();
  }

  if (tipoCambioBtn) {
    tipoCambioBtn.addEventListener('click', loadTipoCambio);
  }

  if (ingresoForm) {
    ingresoForm.addEventListener('submit', (e) => {
      if (!validateFechaIngresoHoy()) {
        e.preventDefault();
      }

      if (!hasAtLeastOneDetalle()) {
        e.preventDefault();
        showAlert('error', 'Debes agregar al menos una línea de detalle para guardar el ingreso.');
      }

      if (monedaSelect && monedaSelect.value === 'USD' && (!tipoCambioInput || !tipoCambioInput.value)) {
        e.preventDefault();
        showAlert('error', 'Para USD debes indicar o actualizar el tipo de cambio.');
      }
    });
  }

  log('Script inicializado', {
    prefix: getFormsetPrefix(),
    totalFormsInput: Boolean(getTotalFormsInput()),
    fechaInput: Boolean(fechaIngresoInput),
  });
})();
