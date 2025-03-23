// Генерация меток времени для месяцев с 2023 по 2025
function generateLabels(start, count, isDaily = false) {
  const labels = [];
  let current = new Date(start);
  if (isDaily) {
    // Генерация ежедневных меток для января 2025
    for (let i = 1; i <= 31; i++) {
      labels.push('2025-01-' + (i < 10 ? '0' + i : i));
    }
  } else {
    for (let i = 0; i < count; i++) {
      const month = current.getMonth() + 1;
      const year = current.getFullYear();
      labels.push(year + '-' + (month < 10 ? '0' + month : month));
      current.setMonth(current.getMonth() + 1);
    }
  }
  return labels;
}

// Функция для объединения массивов данных по годам
function combineYearlyData(yearlyData) {
  return [...yearlyData["2023"], ...yearlyData["2024"], ...yearlyData["2025"]];
}

// Функция для получения данных в зависимости от интервала
function getDataForInterval(data, interval) {
  if (interval === '1m') {
    return data.daily_2025_01 || [];
  }
  return combineYearlyData(data);
}

// Функция для создания конфигурации графика
function createChartConfig(type, data, options = {}) {
  return {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: { tooltip: { enabled: true }, legend: { position: 'bottom' } },
      scales: {
        x: {
          display: true,
          title: { display: true, text: 'Месяц' }
        },
        y: {
          ...options.y,
          display: true,
          title: { display: true, text: options.yAxisTitle || 'Курс' }
        }
      },
      ...options
    }
  };
}

// Загрузка данных и инициализация графиков
async function initializeCharts() {
  try {
    const response = await fetch('exchangerates.json');
    const data = await response.json();
    let baseLabels = generateLabels("2023-01-01", 36);
    let cryptoChart, fiatChart;

    // Функция обновления графиков
    function updateCharts(interval) {
      const isDaily = interval === '1m';
      const labels = isDaily ? generateLabels(null, null, true) : baseLabels.slice(-getMonthCount(interval));

      // Подготовка данных для криптовалют
      const cryptoDatasets = Object.keys(data.crypto).map(currency => ({
        label: currency,
        data: getDataForInterval(data.crypto[currency], interval),
        borderColor: data.colors[currency].borderColor,
        backgroundColor: data.colors[currency].backgroundColor,
        tension: 0.3
      }));

      // Подготовка данных для фиатных валют
      const fiatDatasets = Object.keys(data.fiat).map(currency => ({
        label: currency,
        data: getDataForInterval(data.fiat[currency], interval),
        borderColor: data.colors[currency].borderColor,
        backgroundColor: data.colors[currency].backgroundColor,
        tension: 0.3
      }));

      // Обновление графиков
      if (!cryptoChart) {
        const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
        cryptoChart = new Chart(cryptoCtx, createChartConfig('line', {
          labels: labels,
          datasets: cryptoDatasets
        }, {
          y: {
            type: 'logarithmic',
            ticks: {
              callback: function(value) {
                return value;
              }
            }
          },
          yAxisTitle: 'Курс (USD)'
        }));
      } else {
        cryptoChart.data.labels = labels;
        cryptoChart.data.datasets = cryptoDatasets;
        cryptoChart.update();
      }

      if (!fiatChart) {
        const fiatCtx = document.getElementById('fiatChart').getContext('2d');
        fiatChart = new Chart(fiatCtx, createChartConfig('line', {
          labels: labels,
          datasets: fiatDatasets
        }));
      } else {
        fiatChart.data.labels = labels;
        fiatChart.data.datasets = fiatDatasets;
        fiatChart.update();
      }
    }

    // Функция определения количества месяцев для интервала
    function getMonthCount(interval) {
      switch(interval) {
        case '1m': return 1;
        case '6m': return 6;
        case '1y': return 12;
        case '3y': return 36;
        default: return 36;
      }
    }

    // Инициализация с дефолтным интервалом
    updateCharts('3y');

    // Обработчик изменения интервала
    document.getElementById('timeRange').addEventListener('change', (e) => {
      updateCharts(e.target.value);
    });

  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
    alert('Произошла ошибка при загрузке данных. Пожалуйста, обновите страницу.');
  }
}

// Запуск инициализации при загрузке страницы
window.addEventListener('load', initializeCharts); 