Я помогу добавить детальные ежедневные данные в `exchangerates.json` и обновлю `frontpage.html` для корректного отображения месячного интервала.

Сначала обновим `exchangerates.json`:

```json:ai_experiments/exchangerates.json
{
  "crypto": {
    "BTC": {
      "2023": [21000, 22000, 23000, 22500, 22000, 21500, 21000, 21800, 22500, 23000, 24000, 23500],
      "2024": [25000, 26000, 25500, 26500, 27000, 27500, 28000, 28500, 29000, 29500, 30000, 31000],
      "2025": [32000, 31500, 31000, 30500, 31000, 31500, 32000, 32500, 33000, 33500, 34000, 34500],
      "daily_2025_01": [
        32000, 32100, 32200, 32150, 32300, 32250, 32400, 32350, 32500, 32450,
        32600, 32550, 32700, 32650, 32800, 32750, 32900, 32850, 33000, 32950,
        33100, 33050, 33200, 33150, 33300, 33250, 33400, 33350, 33500, 33450, 33600
      ]
    },
    "ETH": {
      "2023": [1600, 1650, 1700, 1680, 1660, 1640, 1620, 1630, 1650, 1670, 1700, 1690],
      "2024": [1720, 1750, 1740, 1760, 1780, 1800, 1820, 1840, 1850, 1870, 1900, 1920],
      "2025": [1950, 1940, 1930, 1920, 1910, 1900, 1890, 1880, 1870, 1860, 1850, 1840],
      "daily_2025_01": [
        1950, 1955, 1960, 1958, 1965, 1963, 1970, 1968, 1975, 1973,
        1980, 1978, 1985, 1983, 1990, 1988, 1995, 1993, 2000, 1998,
        2005, 2003, 2010, 2008, 2015, 2013, 2020, 2018, 2025, 2023, 2030
      ]
    },
    "TON": {
      "2023": [1.00, 1.02, 1.05, 1.03, 1.01, 1.00, 0.98, 1.00, 1.02, 1.03, 1.05, 1.04],
      "2024": [1.06, 1.08, 1.07, 1.09, 1.10, 1.11, 1.10, 1.09, 1.08, 1.07, 1.06, 1.05],
      "2025": [1.04, 1.03, 1.02, 1.01, 1.00, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93],
      "daily_2025_01": [
        1.04, 1.045, 1.05, 1.048, 1.052, 1.05, 1.055, 1.053, 1.058, 1.056,
        1.06, 1.058, 1.062, 1.06, 1.065, 1.063, 1.068, 1.066, 1.07, 1.068,
        1.072, 1.07, 1.075, 1.073, 1.078, 1.076, 1.08, 1.078, 1.082, 1.08, 1.085
      ]
    }
  },
  "fiat": {
    "RUB/EUR": {
      "2023": [90.0, 90.5, 91.0, 91.5, 92.0, 92.5, 93.0, 93.5, 94.0, 94.5, 95.0, 95.5],
      "2024": [96.0, 96.5, 97.0, 97.5, 98.0, 98.5, 99.0, 99.5, 100.0, 100.5, 101.0, 101.5],
      "2025": [102.0, 102.5, 103.0, 103.5, 104.0, 104.5, 105.0, 105.5, 106.0, 106.5, 107.0, 107.5],
      "daily_2025_01": [
        102.0, 102.1, 102.2, 102.3, 102.4, 102.5, 102.6, 102.7, 102.8, 102.9,
        103.0, 103.1, 103.2, 103.3, 103.4, 103.5, 103.6, 103.7, 103.8, 103.9,
        104.0, 104.1, 104.2, 104.3, 104.4, 104.5, 104.6, 104.7, 104.8, 104.9, 105.0
      ]
    },
    "RUB/USD": {
      "2023": [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81],
      "2024": [82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93],
      "2025": [94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105],
      "daily_2025_01": [
        94.0, 94.2, 94.4, 94.6, 94.8, 95.0, 95.2, 95.4, 95.6, 95.8,
        96.0, 96.2, 96.4, 96.6, 96.8, 97.0, 97.2, 97.4, 97.6, 97.8,
        98.0, 98.2, 98.4, 98.6, 98.8, 99.0, 99.2, 99.4, 99.6, 99.8, 100.0
      ]
    },
    "AED": {
      "2023": [3.67, 3.67, 3.68, 3.68, 3.69, 3.69, 3.70, 3.70, 3.71, 3.71, 3.72, 3.72],
      "2024": [3.73, 3.73, 3.74, 3.74, 3.75, 3.75, 3.76, 3.76, 3.77, 3.77, 3.78, 3.78],
      "2025": [3.79, 3.79, 3.80, 3.80, 3.81, 3.81, 3.82, 3.82, 3.83, 3.83, 3.84, 3.84],
      "daily_2025_01": [
        3.79, 3.791, 3.792, 3.793, 3.794, 3.795, 3.796, 3.797, 3.798, 3.799,
        3.80, 3.801, 3.802, 3.803, 3.804, 3.805, 3.806, 3.807, 3.808, 3.809,
        3.81, 3.811, 3.812, 3.813, 3.814, 3.815, 3.816, 3.817, 3.818, 3.819, 3.82
      ]
    },
    "CNY": {
      "2023": [6.45, 6.46, 6.47, 6.48, 6.49, 6.50, 6.51, 6.52, 6.53, 6.54, 6.55, 6.56],
      "2024": [6.57, 6.58, 6.59, 6.60, 6.61, 6.62, 6.63, 6.64, 6.65, 6.66, 6.67, 6.68],
      "2025": [6.69, 6.70, 6.71, 6.72, 6.73, 6.74, 6.75, 6.76, 6.77, 6.78, 6.79, 6.80],
      "daily_2025_01": [
        6.69, 6.692, 6.694, 6.696, 6.698, 6.70, 6.702, 6.704, 6.706, 6.708,
        6.71, 6.712, 6.714, 6.716, 6.718, 6.72, 6.722, 6.724, 6.726, 6.728,
        6.73, 6.732, 6.734, 6.736, 6.738, 6.74, 6.742, 6.744, 6.746, 6.748, 6.75
      ]
    }
  },
  "colors": {
    "BTC": {
      "borderColor": "#ff9800",
      "backgroundColor": "rgba(255,152,0,0.1)"
    },
    "ETH": {
      "borderColor": "#007bff",
      "backgroundColor": "rgba(0,123,255,0.1)"
    },
    "TON": {
      "borderColor": "#28a745",
      "backgroundColor": "rgba(40,167,69,0.1)"
    },
    "RUB/EUR": {
      "borderColor": "#6f42c1",
      "backgroundColor": "rgba(111,66,193,0.1)"
    },
    "RUB/USD": {
      "borderColor": "#007bff",
      "backgroundColor": "rgba(0,123,255,0.1)"
    },
    "AED": {
      "borderColor": "#ff5722",
      "backgroundColor": "rgba(255,87,34,0.1)"
    },
    "CNY": {
      "borderColor": "#28a745",
      "backgroundColor": "rgba(40,167,69,0.1)"
    }
  }
}
```
Теперь обновим `frontpage.html`, чтобы добавить поддержку ежедневных данных:

```html:ai_experiments/frontpage.html
// ... existing code ...
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
// ... existing code ...
```
Я внес следующие изменения:

1. В `exchangerates.json`:
   - Добавил ежедневные данные для января 2025 года для всех валют
   - Данные хранятся в новых полях `daily_2025_01`
   - Для каждой валюты добавлено 31 значение (по дням)

2. В `frontpage.html`:
   - Обновил функцию `generateLabels` для поддержки ежедневных меток
   - Добавил функцию `getDataForInterval` для выбора правильного набора данных
   - Реорганизовал код для более эффективного обновления графиков
   - Добавил поддержку переключения между месячными и ежедневными данными

Теперь при выборе интервала "1 месяц" графики будут показывать ежедневные данные за январь 2025 года, а при выборе других интервалов - помесячные данные за соответствующий период.

Хотите ли вы внести какие-либо дополнительные изменения в отображение данных или функциональность графиков?
