(function () {
  const messages = window.INGRESOS_MESSAGES || [];
  if (!window.Swal || !Array.isArray(messages) || messages.length === 0) return;

  const mapIcon = (level) => {
    if (level.includes('success')) return 'success';
    if (level.includes('error') || level.includes('danger')) return 'error';
    if (level.includes('warning')) return 'warning';
    return 'info';
  };

  messages.forEach((msg) => {
    Swal.fire({
      icon: mapIcon((msg.level || '').toLowerCase()),
      text: msg.text || '',
      confirmButtonText: 'Entendido',
      timer: 3500,
      timerProgressBar: true,
    });
  });
})();
