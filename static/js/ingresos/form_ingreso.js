(function () {
  const addBtn = document.getElementById('add-detalle');
  const container = document.getElementById('detalles-container');
  const totalForms = document.getElementById('id_detalleingreso_set-TOTAL_FORMS');
  if (!addBtn || !container || !totalForms) return;

  addBtn.addEventListener('click', () => {
    const index = parseInt(totalForms.value, 10);
    const html = `
      <div class="detalle-row row g-2 mb-2 border-bottom pb-2">
        <div class="col-md-4"><input type="text" name="detalleingreso_set-${index}-descripcion" maxlength="200" required id="id_detalleingreso_set-${index}-descripcion"></div>
        <div class="col-md-2"><input type="number" name="detalleingreso_set-${index}-cantidad" step="0.01" required id="id_detalleingreso_set-${index}-cantidad"></div>
        <div class="col-md-2"><input type="number" name="detalleingreso_set-${index}-precio_unitario" step="0.01" required id="id_detalleingreso_set-${index}-precio_unitario"></div>
        <div class="col-md-2"><input type="number" name="detalleingreso_set-${index}-porcentaje_iva" step="0.01" value="13" required id="id_detalleingreso_set-${index}-porcentaje_iva"></div>
        <div class="col-md-2"><input type="checkbox" name="detalleingreso_set-${index}-DELETE" id="id_detalleingreso_set-${index}-DELETE"> Eliminar</div>
      </div>`;
    container.insertAdjacentHTML('beforeend', html);
    totalForms.value = index + 1;
  });
})();
