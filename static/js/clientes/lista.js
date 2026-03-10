(function () {
  const hasSwal = typeof window.Swal !== 'undefined' && typeof window.Swal.fire === 'function';

  const mapIcon = (tags) => {
    if ((tags || '').includes('success')) return 'success';
    if ((tags || '').includes('warning')) return 'warning';
    if ((tags || '').includes('error')) return 'error';
    return 'info';
  };

  const mapTitle = (text) => {
    const normalized = String(text || '').toLowerCase();
    if (normalized.includes('creado')) return 'Cliente guardado';
    if (normalized.includes('actualizado')) return 'Cliente actualizado';
    if (normalized.includes('eliminado')) return 'Cliente eliminado';
    return 'Clientes';
  };

  const msgNode = document.getElementById('clientes-messages');
  if (msgNode && hasSwal) {
    try {
      const mensajes = JSON.parse(msgNode.textContent || '[]');
      if (mensajes.length === 1) {
        const m = mensajes[0];
        Swal.fire({
          icon: mapIcon(m.tags),
          title: mapTitle(m.text),
          text: m.text,
          confirmButtonText: 'Entendido',
        });
      } else if (mensajes.length > 1) {
        const html = `<ul style="text-align:left; padding-left:1rem; margin:0;">${mensajes
          .map((m) => `<li>${m.text}</li>`)
          .join('')}</ul>`;
        Swal.fire({
          icon: mensajes.some((m) => mapIcon(m.tags) === 'error') ? 'error' : 'info',
          title: 'Mensajes del sistema',
          html,
          confirmButtonText: 'Entendido',
        });
      }
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
