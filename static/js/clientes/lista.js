(function () {
  const hasSwal = typeof window.Swal !== 'undefined' && typeof window.Swal.fire === 'function';

  const mapIcon = (tags) => {
    if ((tags || '').includes('success')) return 'success';
    if ((tags || '').includes('warning')) return 'warning';
    if ((tags || '').includes('error')) return 'error';
    return 'info';
  };

  const msgNode = document.getElementById('clientes-messages');
  if (msgNode && hasSwal) {
    try {
      const mensajes = JSON.parse(msgNode.textContent || '[]');
      mensajes.forEach((m) => {
        Swal.fire({
          toast: true,
          position: 'top-end',
          timer: 2800,
          showConfirmButton: false,
          icon: mapIcon(m.tags),
          title: m.text,
        });
      });
    } catch (_) {}
  }

  document.querySelectorAll('.js-eliminar-cliente').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      if (!hasSwal) return;
      event.preventDefault();
      const cliente = form.dataset.cliente || 'este cliente';
      const res = await Swal.fire({
        icon: 'warning',
        title: 'Eliminar cliente',
        text: `¿Desea eliminar a ${cliente}? Esta acción no se puede deshacer.`,
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
      });
      if (res.isConfirmed) form.submit();
    });
  });
})();
