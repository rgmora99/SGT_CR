(function () {
  const addBtn = document.getElementById('add-detalle');
  const container = document.getElementById('detalles-container');
  const totalForms = document.getElementById('id_detalleingreso_set-TOTAL_FORMS');
  const ingresoForm = document.getElementById('ingreso-form');
  const monedaSelect = document.getElementById('id_moneda');
  const fechaIngresoInput = document.getElementById('id_fecha_ingreso');
  const tipoCambioWrap = document.querySelector('.js-tipo-cambio-wrap');
  const tipoCambioInput = document.getElementById('id_tipo_cambio');
  const tipoCambioBtn = document.getElementById('btnTipoCambioAuto');
  const tipoCambioSource = document.getElementById('tipoCambioSource');

  const showAlert = (icon, text) => {
    if (window.Swal) {
      window.Swal.fire({ icon, text, confirmButtonText: 'Entendido' });
    } else {
      alert(text);
    }
  };

  const showToast = (icon, title) => {
    if (window.Swal) {
      window.Swal.fire({
        icon,
        title,
        toast: true,
        position: 'top-end',
        timer: 1800,
        showConfirmButton: false,
        timerProgressBar: true,
      });
    }
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
    if (!addBtn || !container || !totalForms) return;
    const index = Number(totalForms.value || 0);

    const firstProducto = container.querySelector('select[name$="-producto"]');
    const productOptions = firstProducto ? firstProducto.innerHTML : '<option value="">---------</option>';

    const html = `
      <div class="detalle-row row g-2 mb-2 border-bottom pb-2">
        <div class="col-md-3"><select class="form-select js-producto" name="detalleingreso_set-${index}-producto" id="id_detalleingreso_set-${index}-producto">${productOptions}</select></div>
        <div class="col-md-3"><input type="text" class="form-control" name="detalleingreso_set-${index}-descripcion" maxlength="200" placeholder="Detalle del servicio o producto" id="id_detalleingreso_set-${index}-descripcion"></div>
        <div class="col-md-2"><input type="number" class="form-control" name="detalleingreso_set-${index}-cantidad" step="0.01" min="0.01" placeholder="Cantidad" id="id_detalleingreso_set-${index}-cantidad"></div>
        <div class="col-md-2"><input type="number" class="form-control" name="detalleingreso_set-${index}-precio_unitario" step="0.01" min="0" placeholder="Precio unitario" id="id_detalleingreso_set-${index}-precio_unitario"></div>
        <div class="col-md-1"><input type="number" class="form-control" name="detalleingreso_set-${index}-porcentaje_iva" step="0.01" min="0" value="13" id="id_detalleingreso_set-${index}-porcentaje_iva"></div>
        <div class="col-md-1 d-flex align-items-center"><input type="checkbox" class="form-check-input" name="detalleingreso_set-${index}-DELETE" id="id_detalleingreso_set-${index}-DELETE"></div>
      </div>`;

    container.insertAdjacentHTML('beforeend', html);
    totalForms.value = index + 1;
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
    const today = new Date().toISOString().slice(0, 10);
    if (fechaIngresoInput.value !== today) {
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
      showToast('success', 'Tipo de cambio actualizado');
    } catch (error) {
      showAlert('warning', error.message || 'No fue posible obtener tipo de cambio automático.');
    }
  };

  if (addBtn) {
    addBtn.addEventListener('click', addDetalleLinea);
  }

  if (fechaIngresoInput) {
    const today = new Date().toISOString().slice(0, 10);
    fechaIngresoInput.min = today;
    fechaIngresoInput.max = today;
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
})();
