(function () {
  const addBtn = document.getElementById('add-detalle');
  const container = document.getElementById('detalles-container');
  const totalForms = document.getElementById('id_detalleingreso_set-TOTAL_FORMS');
  if (!addBtn || !container || !totalForms) return;

  const firstProducto = container.querySelector('select[name$="-producto"]');
  const productOptions = firstProducto ? firstProducto.innerHTML : '<option value="">---------</option>';

  const buildRow = (index) => `
    <div class="detalle-row row g-2 mb-2 border-bottom pb-2">
      <div class="col-md-3"><select class="form-select js-producto" name="detalleingreso_set-${index}-producto" id="id_detalleingreso_set-${index}-producto">${productOptions}</select></div>
      <div class="col-md-3"><input type="text" class="form-control" name="detalleingreso_set-${index}-descripcion" maxlength="200" placeholder="Detalle del servicio o producto" id="id_detalleingreso_set-${index}-descripcion"></div>
      <div class="col-md-2"><input type="number" class="form-control" name="detalleingreso_set-${index}-cantidad" step="0.01" min="0.01" placeholder="Cantidad" required id="id_detalleingreso_set-${index}-cantidad"></div>
      <div class="col-md-2"><input type="number" class="form-control" name="detalleingreso_set-${index}-precio_unitario" step="0.01" min="0" placeholder="Precio unitario" required id="id_detalleingreso_set-${index}-precio_unitario"></div>
      <div class="col-md-1"><input type="number" class="form-control" name="detalleingreso_set-${index}-porcentaje_iva" step="0.01" min="0" value="13" required id="id_detalleingreso_set-${index}-porcentaje_iva"></div>
      <div class="col-md-1 d-flex align-items-center"><input type="checkbox" class="form-check-input" name="detalleingreso_set-${index}-DELETE" id="id_detalleingreso_set-${index}-DELETE"></div>
    </div>`;

  addBtn.addEventListener('click', () => {
    const index = parseInt(totalForms.value, 10);
    container.insertAdjacentHTML('beforeend', buildRow(index));
    totalForms.value = index + 1;
  });
})();
