/* =========================================================
   CIAN CCR — Lógica para "Informes y Reportes"
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  // === GRÁFICO DE EVOLUCIÓN DE CONTRATOS POR MES ===
  const ctx1 = document.getElementById("contratosChart");
  if (ctx1) {
    new Chart(ctx1, {
      type: 'line',
      data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic'],
        datasets: [{
          label: 'Contratos activos',
          data: [40, 42, 45, 49, 52, 54, 55, 57, 59, 61, 63, 64],
          fill: true,
          backgroundColor: 'rgba(0,48,87,0.08)',
          borderColor: '#003057',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: '#003057'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // ✅ permite que use la altura del contenedor
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            ticks: { color: '#6b7280' },
            grid: { display: false }
          },
          y: {
            ticks: { color: '#6b7280' },
            grid: { color: 'rgba(0,0,0,0.05)' }
          }
        }
      }
    });
  }

  // === GRÁFICO DE DISTRIBUCIÓN POR ESTADO ===
  const ctx2 = document.getElementById("estadosChart");
  if (ctx2) {
    new Chart(ctx2, {
      type: 'doughnut',
      data: {
        labels: ['Activos', 'En prórroga', 'Vencidos'],
        datasets: [{
          data: [54, 15, 13],
          backgroundColor: ['#78BE21', '#FFC107', '#DC3545'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // ✅ mismo truco para el doughnut
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#6b7280',
              boxWidth: 14,
              font: { size: 11 }
            }
          }
        },
        cutout: '65%'
      }
    });
  }
});
