(function () {
  const hasSwal = typeof window.Swal !== 'undefined';
  const form = document.getElementById('factura-form');
  if (!form) return;

  const stockApiInput = document.getElementById('stock-api-url');
  const lineasJsonInput = document.getElementById('lineas-json');
  const productosDataScript = document.getElementById('productos-data');
  const consecutivosPorTipoScript = document.getElementById('consecutivos-por-tipo');
  const tipoComprobante = form.querySelector('[name="tipo_comprobante"]');
  const consecutivoCr = document.getElementById('consecutivo-cr');
  const moneda = form.querySelector('[name="moneda"]');
  const tipoCambio = form.querySelector('[name="tipo_cambio"]');
  const fechaEmision = form.querySelector('[name="fecha_emision"]');
  const fechaVencimiento = form.querySelector('[name="fecha_vencimiento"]');
  const almacen = form.querySelector('[name="almacen"]');
  const emitir = form.querySelector('[name="emitir"]');

  const productoInput = document.getElementById('linea-producto');
  const cantidadInput = document.getElementById('linea-cantidad');
  const descuentoInput = document.getElementById('linea-descuento');
  const btnAgregar = document.getElementById('btn-agregar-linea');
  const tablaBody = document.querySelector('#tabla-lineas tbody');
  const totalFactura = document.getElementById('total-factura');
  const resumenMoneda = document.getElementById('resumen-moneda');

  const productos = JSON.parse(productosDataScript?.textContent || '[]');
  const consecutivosPorTipo = JSON.parse(consecutivosPorTipoScript?.textContent || '{}');
  const productosMap = new Map(productos.map((p) => [String(p.id), p]));
  const lineas = [];

  function alerta(icon, text) {
    if (!hasSwal) return;
    Swal.fire({ icon, text, confirmButtonText: 'Entendido' });
  }

  function toNum(value) {
    const n = Number(String(value || '').replace(',', '.'));
    return Number.isFinite(n) ? n : NaN;
  }

  function todayISO() {
    return new Date().toISOString().split('T')[0];
  }

  function monedaActual() {
    return (moneda.value || 'CRC').toUpperCase();
  }

  function tipoCambioActual() {
    const tc = toNum(tipoCambio.value);
    return Number.isFinite(tc) && tc > 0 ? tc : NaN;
  }

  function precioMostrado(linea) {
    const m = monedaActual();
    if (m === 'USD') {
      const tc = tipoCambioActual();
      if (!Number.isFinite(tc)) return NaN;
      return linea.precio_crc / tc;
    }
    return linea.precio_crc;
  }

  function calcularTotalLinea(linea) {
    const precio = precioMostrado(linea);
    const subtotal = linea.cantidad * precio;
    const descuentoMonto = subtotal * (linea.descuento / 100);
    const base = subtotal - descuentoMonto;
    const impuestoMonto = base * (linea.impuesto / 100);
    return base + impuestoMonto;
  }

  function renderLineas() {
    tablaBody.innerHTML = '';
    let total = 0;

    lineas.forEach((linea, idx) => {
      const precio = precioMostrado(linea);
      const totalLinea = calcularTotalLinea(linea);
      total += Number.isFinite(totalLinea) ? totalLinea : 0;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${linea.codigo} - ${linea.nombre}</td>
        <td class="text-end">${linea.cantidad.toFixed(3)}</td>
        <td class="text-end">${Number.isFinite(precio) ? precio.toFixed(2) : '---'}</td>
        <td class="text-end">${linea.descuento.toFixed(2)}</td>
        <td class="text-end">${linea.impuesto.toFixed(2)}</td>
        <td class="text-end">${Number.isFinite(totalLinea) ? totalLinea.toFixed(2) : '---'}</td>
        <td class="text-end"><button type="button" class="btn btn-sm btn-outline-danger" data-remove="${idx}">Quitar</button></td>
      `;
      tablaBody.appendChild(tr);
    });

    if (resumenMoneda) resumenMoneda.textContent = monedaActual();
    totalFactura.textContent = total.toFixed(2);
    lineasJsonInput.value = JSON.stringify(lineas.map((l) => ({
      producto_id: l.id,
      cantidad: l.cantidad,
      descuento: l.descuento,
    })));
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

    if (!lineas.length) {
      alerta('warning', 'Debes agregar al menos una línea de detalle.');
      return false;
    }

    const monedaVal = (moneda.value || '').trim().toUpperCase();
    if (!['CRC', 'USD'].includes(monedaVal)) {
      alerta('error', 'La moneda seleccionada no es válida.');
      return false;
    }

    if (monedaVal === 'USD') {
      const tc = toNum(tipoCambio.value);
      if (!Number.isFinite(tc) || tc <= 0) {
        alerta('warning', 'Para facturas en USD debes indicar un tipo de cambio mayor a cero.');
        tipoCambio.focus();
        return false;
      }
    }

    if (!fechaEmision.value) {
      alerta('warning', 'Debes indicar fecha de emisión.');
      return false;
    }

    if (fechaEmision.value > todayISO()) {
      alerta('warning', 'La fecha de emisión no puede ser futura.');
      return false;
    }

    if (fechaVencimiento.value && fechaVencimiento.value < fechaEmision.value) {
      alerta('warning', 'La fecha de vencimiento no puede ser menor a la fecha de emisión.');
      return false;
    }

    return true;
  }

  async function validarStockAntesEmitir() {
    if (!emitir?.checked) return true;

    const requeridas = new Map();
    for (const linea of lineas) {
      if (!linea.maneja_inventario) continue;
      requeridas.set(linea.id, (requeridas.get(linea.id) || 0) + linea.cantidad);
    }

    for (const [productoId, cantidadReq] of requeridas.entries()) {
      const params = new URLSearchParams({
        producto_id: String(productoId),
        almacen_id: almacen.value || '',
      });
      const resp = await fetch(`${stockApiInput.value}?${params.toString()}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      const data = await resp.json();
      if (!resp.ok || !data.ok) {
        alerta('error', data.error || 'No fue posible validar stock.');
        return false;
      }

      if (!data.maneja_inventario) continue;

      const stock = toNum(data.stock_libre);
      if (stock < cantidadReq) {
        alerta('error', `Stock insuficiente para ${data.producto}. Disponible: ${data.stock_libre}. Solicitado: ${cantidadReq.toFixed(3)}.`);
        return false;
      }
    }

    return true;
  }

  btnAgregar?.addEventListener('click', function () {
    const productoId = productoInput.value;
    const producto = productosMap.get(productoId);
    if (!producto) {
      alerta('warning', 'Debes seleccionar un producto o servicio.');
      return;
    }

    const cantidad = toNum(cantidadInput.value);
    const descuento = toNum(descuentoInput.value || '0');
    if (!Number.isFinite(cantidad) || cantidad <= 0) {
      alerta('warning', 'La cantidad debe ser mayor a cero.');
      return;
    }
    if (!Number.isFinite(descuento) || descuento < 0 || descuento > 100) {
      alerta('warning', 'El descuento debe estar entre 0 y 100.');
      return;
    }

    lineas.push({
      id: Number(producto.id),
      codigo: producto.codigo,
      nombre: producto.nombre,
      precio_crc: toNum(producto.precio),
      impuesto: toNum(producto.impuesto || '0'),
      maneja_inventario: !!producto.maneja_inventario,
      cantidad,
      descuento,
    });

    renderLineas();
  });

  tablaBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-remove]');
    if (!btn) return;
    const idx = Number(btn.getAttribute('data-remove'));
    if (Number.isInteger(idx) && idx >= 0) {
      lineas.splice(idx, 1);
      renderLineas();
    }
  });


  tipoComprobante?.addEventListener('change', function () {
    const cod = tipoComprobante.value;
    if (consecutivosPorTipo[cod] && consecutivoCr) {
      consecutivoCr.value = consecutivosPorTipo[cod];
    }
  });

  moneda?.addEventListener('change', function () {
    renderLineas();
  });

  tipoCambio?.addEventListener('input', function () {
    if (monedaActual() === 'USD') renderLineas();
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!validarFormulario()) return;
    const stockOk = await validarStockAntesEmitir();
    if (!stockOk) return;
    renderLineas();
    form.submit();
  });
})();
