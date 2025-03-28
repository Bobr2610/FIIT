Я помогу создать отдельный JSON файл для хранения данных и обновлю код для их загрузки.

Сначала создадим файл с данными:

```json:ai_experiments/exchangerates.json
{
  "crypto": {
    "BTC": {
      "2023": [21000, 22000, 23000, 22500, 22000, 21500, 21000, 21800, 22500, 23000, 24000, 23500],
      "2024": [25000, 26000, 25500, 26500, 27000, 27500, 28000, 28500, 29000, 29500, 30000, 31000],
      "2025": [32000, 31500, 31000, 30500, 31000, 31500, 32000, 32500, 33000, 33500, 34000, 34500]
    },
    "ETH": {
      "2023": [1600, 1650, 1700, 1680, 1660, 1640, 1620, 1630, 1650, 1670, 1700, 1690],
      "2024": [1720, 1750, 1740, 1760, 1780, 1800, 1820, 1840, 1850, 1870, 1900, 1920],
      "2025": [1950, 1940, 1930, 1920, 1910, 1900, 1890, 1880, 1870, 1860, 1850, 1840]
    },
    "TON": {
      "2023": [1.00, 1.02, 1.05, 1.03, 1.01, 1.00, 0.98, 1.00, 1.02, 1.03, 1.05, 1.04],
      "2024": [1.06, 1.08, 1.07, 1.09, 1.10, 1.11, 1.10, 1.09, 1.08, 1.07, 1.06, 1.05],
      "2025": [1.04, 1.03, 1.02, 1.01, 1.00, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93]
    }
  },
  "fiat": {
    "RUB/EUR": {
      "2023": [90.0, 90.5, 91.0, 91.5, 92.0, 92.5, 93.0, 93.5, 94.0, 94.5, 95.0, 95.5],
      "2024": [96.0, 96.5, 97.0, 97.5, 98.0, 98.5, 99.0, 99.5, 100.0, 100.5, 101.0, 101.5],
      "2025": [102.0, 102.5, 103.0, 103.5, 104.0, 104.5, 105.0, 105.5, 106.0, 106.5, 107.0, 107.5]
    },
    "RUB/USD": {
      "2023": [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81],
      "2024": [82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93],
      "2025": [94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105]
    },
    "AED": {
      "2023": [3.67, 3.67, 3.68, 3.68, 3.69, 3.69, 3.70, 3.70, 3.71, 3.71, 3.72, 3.72],
      "2024": [3.73, 3.73, 3.74, 3.74, 3.75, 3.75, 3.76, 3.76, 3.77, 3.77, 3.78, 3.78],
      "2025": [3.79, 3.79, 3.80, 3.80, 3.81, 3.81, 3.82, 3.82, 3.83, 3.83, 3.84, 3.84]
    },
    "CNY": {
      "2023": [6.45, 6.46, 6.47, 6.48, 6.49, 6.50, 6.51, 6.52, 6.53, 6.54, 6.55, 6.56],
      "2024": [6.57, 6.58, 6.59, 6.60, 6.61, 6.62, 6.63, 6.64, 6.65, 6.66, 6.67, 6.68],
      "2025": [6.69, 6.70, 6.71, 6.72, 6.73, 6.74, 6.75, 6.76, 6.77, 6.78, 6.79, 6.80]
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
Теперь обновим код в HTML файле для загрузки данных из JSON:

```html:ai_experiments/frontpage.html
// ... existing code ...
  <!-- JavaScript для Chart.js и имитации обновления данных -->
  <script>
    // Генерация меток времени для месяцев с 2023 по 2025
    function generateLabels(start, count) {
      const labels = [];
      let current = new Date(start);
      for (let i = 0; i < count; i++) {
        const month = current.getMonth() + 1;
        const year = current.getFullYear();
        labels.push(year + '-' + (month < 10 ? '0' + month : month));
        current.setMonth(current.getMonth() + 1);
      }
      return labels;
    }

    // Функция для объединения массивов данных по годам
    function combineYearlyData(yearlyData) {
      return [...yearlyData["2023"], ...yearlyData["2024"], ...yearlyData["2025"]];
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
        const baseLabels = generateLabels("2023-01-01", 36);

        // Подготовка данных для криптовалют
        const cryptoDatasets = Object.keys(data.crypto).map(currency => ({
          label: currency,
          data: combineYearlyData(data.crypto[currency]),
          borderColor: data.colors[currency].borderColor,
          backgroundColor: data.colors[currency].backgroundColor,
          tension: 0.3
        }));

        // Подготовка данных для фиатных валют
        const fiatDatasets = Object.keys(data.fiat).map(currency => ({
          label: currency,
          data: combineYearlyData(data.fiat[currency]),
          borderColor: data.colors[currency].borderColor,
          backgroundColor: data.colors[currency].backgroundColor,
          tension: 0.3
        }));

        // Инициализация графика криптовалют
        const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
        const cryptoChart = new Chart(cryptoCtx, createChartConfig('line', {
          labels: baseLabels,
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

        // Инициализация графика фиатных валют
        const fiatCtx = document.getElementById('fiatChart').getContext('2d');
        const fiatChart = new Chart(fiatCtx, createChartConfig('line', {
          labels: baseLabels,
          datasets: fiatDatasets
        }));

        // Обработчик изменения интервала
        document.getElementById('timeRange').addEventListener('change', (e) => {
          let range;
          switch(e.target.value) {
            case '1m': range = 1; break;
            case '6m': range = 6; break;
            case '1y': range = 12; break;
            case '3y': range = 36; break;
            default: range = 36;
          }

          // Обновление данных для обоих графиков
          const newLabels = baseLabels.slice(-range);

          cryptoChart.data.labels = newLabels;
          cryptoChart.data.datasets.forEach(dataset => {
            dataset.data = cryptoDatasets.find(d => d.label === dataset.label).data.slice(-range);
          });
          cryptoChart.update();

          fiatChart.data.labels = newLabels;
          fiatChart.data.datasets.forEach(dataset => {
            dataset.data = fiatDatasets.find(d => d.label === dataset.label).data.slice(-range);
          });
          fiatChart.update();
        });

      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        alert('Произошла ошибка при загрузке данных. Пожалуйста, обновите страницу.');
      }
    }

    // Запуск инициализации при загрузке страницы
    window.addEventListener('load', initializeCharts);
  </script>
// ... existing code ...
```
Я внес следующие изменения:

1. Создал отдельный файл `exchangerates.json` с:
   - Данными курсов валют, структурированными по годам
   - Цветовыми схемами для каждой валюты
   - Разделением на криптовалюты и фиатные валюты

2. Обновил JavaScript код в `frontpage.html`:
   - Добавил асинхронную загрузку данных из JSON файла
   - Создал вспомогательные функции:
     - `combineYearlyData` для объединения данных по годам
     - `createChartConfig` для создания конфигурации графиков
   - Реализовал динамическое создание наборов данных из JSON
   - Добавил обработку ошибок при загрузке данных
   - Улучшил обработчик изменения временного интервала

3. Улучшил структуру кода:
   - Вынес повторяющиеся конфигурации в отдельные функции
   - Добавил комментарии для лучшей читаемости
   - Реализовал более гибкую систему обновления данных

Теперь все данные хранятся в отдельном JSON файле, что делает код более поддерживаемым и позволяет легко обновлять данные без изменения основного кода. Также это упрощает добавление новых валют и изменение их параметров.

Хотите ли вы внести какие-либо дополнительные изменения в структуру данных или функциональность?
