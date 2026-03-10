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
  if (!form) return;

  const moneda = form.querySelector('[name="moneda"]');
  const tipoCambio = form.querySelector('[name="tipo_cambio"]');
  const fechaEmision = form.querySelector('[name="fecha_emision"]');
  const fechaVencimiento = form.querySelector('[name="fecha_vencimiento"]');
  const producto = form.querySelector('[name="producto"]');
  const almacen = form.querySelector('[name="almacen"]');
  const cantidad = form.querySelector('[name="cantidad"]');
  const descuento = form.querySelector('[name="porcentaje_descuento"]');
  const emitir = form.querySelector('[name="emitir"]');
  const stockApiInput = document.getElementById('stock-api-url');

  function parseDecimal(value) {
    const parsed = Number(String(value || '').replace(',', '.'));
    return Number.isFinite(parsed) ? parsed : NaN;
  }

  function todayISO() {
    return new Date().toISOString().split('T')[0];
  }

  function validarFormulario() {
    const required = form.querySelectorAll('[required]');
    for (const field of required) {
      if (!field.value || !String(field.value).trim()) {
        field.focus();
        alerta('warning', 'Completa todos los campos obligatorios.');
        return false;
      }
    }

    const monedaVal = (moneda.value || '').trim().toUpperCase();
    if (!['CRC', 'USD'].includes(monedaVal)) {
      alerta('error', 'La moneda seleccionada no es válida.');
      moneda.focus();
      return false;
    }

    if (monedaVal === 'USD') {
      const tc = parseDecimal(tipoCambio.value);
      if (!Number.isFinite(tc) || tc <= 0) {
        alerta('warning', 'Para facturas en USD debes indicar un tipo de cambio mayor a cero.');
        tipoCambio.focus();
        return false;
      }
    }

    if (fechaEmision.value > todayISO()) {
      alerta('warning', 'La fecha de emisión no puede ser futura.');
      fechaEmision.focus();
      return false;
    }

    if (fechaVencimiento.value && fechaVencimiento.value < fechaEmision.value) {
      alerta('warning', 'La fecha de vencimiento no puede ser menor a la fecha de emisión.');
      fechaVencimiento.focus();
      return false;
    }

    const cant = parseDecimal(cantidad.value);
    if (!Number.isFinite(cant) || cant <= 0) {
      alerta('warning', 'La cantidad debe ser mayor a cero.');
      cantidad.focus();
      return false;
    }

    const desc = parseDecimal(descuento.value || '0');
    if (!Number.isFinite(desc) || desc < 0 || desc > 100) {
      alerta('warning', 'El descuento debe estar entre 0 y 100.');
      descuento.focus();
      return false;
    }

    return true;
  }

  async function validarStockAntesEmitir() {
    if (!emitir || !emitir.checked) return true;
    if (!stockApiInput || !stockApiInput.value) return true;

    const productoId = producto.value;
    if (!productoId) return false;

    const params = new URLSearchParams({
      producto_id: productoId,
      almacen_id: almacen.value || '',
    });

    const resp = await fetch(`${stockApiInput.value}?${params.toString()}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    const data = await resp.json();

    if (!resp.ok || !data.ok) {
      alerta('error', data.error || 'No fue posible validar stock en este momento.');
      return false;
    }

    if (!data.maneja_inventario) return true;

    const cant = parseDecimal(cantidad.value);
    const stock = parseDecimal(data.stock_libre);
    if (stock < cant) {
      alerta('error', `Stock insuficiente para ${data.producto}. Disponible: ${data.stock_libre}. Solicitado: ${cantidad.value}.`);
      return false;
    }

    return true;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    if (!validarFormulario()) return;

    const stockOk = await validarStockAntesEmitir();
    if (!stockOk) return;

    form.submit();
  });
})();
