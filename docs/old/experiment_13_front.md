Я интегрирую дополнительные курсы валют и улучшенную реализацию селектора интервалов из `frontpage11.html` в `frontpage.html`.

```html:ai_experiments/frontpage.html
// ... existing code ...
    <!-- Хедер панели (фильтры и выбор темы) -->
    <div class="dashboard-header" id="dashboard">
      <h2>Обзор рынка</h2>
      <div class="time-filter">
        <label for="timeRange">Интервал:</label>
        <select id="timeRange">
          <option value="1m">1 месяц</option>
          <option value="6m">6 месяцев</option>
          <option value="1y">1 год</option>
          <option value="3y" selected>3 года</option>
        </select>
        <label for="colorScheme">Тема:</label>
        <select id="colorScheme">
          <option value="default">Стандартная</option>
          <option value="colorblind">Для дальтоников</option>
        </select>
      </div>
    </div>
// ... existing code ...
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
    const baseLabels = generateLabels("2023-01-01", 36);

    /* --- Данные и конфигурация для графика криптоактивов --- */
    const cryptoData = {
      labels: baseLabels,
      datasets: [
        {
          label: 'BTC',
          data: [
            21000, 22000, 23000, 22500, 22000, 21500, 21000, 21800, 22500, 23000, 24000, 23500,  // 2023
            25000, 26000, 25500, 26500, 27000, 27500, 28000, 28500, 29000, 29500, 30000, 31000,  // 2024
            32000, 31500, 31000, 30500, 31000, 31500, 32000, 32500, 33000, 33500, 34000, 34500   // 2025
          ],
          borderColor: '#ff9800',
          backgroundColor: 'rgba(255,152,0,0.1)',
          tension: 0.3
        },
        {
          label: 'ETH',
          data: [
            1600, 1650, 1700, 1680, 1660, 1640, 1620, 1630, 1650, 1670, 1700, 1690,  // 2023
            1720, 1750, 1740, 1760, 1780, 1800, 1820, 1840, 1850, 1870, 1900, 1920,  // 2024
            1950, 1940, 1930, 1920, 1910, 1900, 1890, 1880, 1870, 1860, 1850, 1840   // 2025
          ],
          borderColor: '#007bff',
          backgroundColor: 'rgba(0,123,255,0.1)',
          tension: 0.3
        },
        {
          label: 'TON',
          data: [
            1.00, 1.02, 1.05, 1.03, 1.01, 1.00, 0.98, 1.00, 1.02, 1.03, 1.05, 1.04,  // 2023
            1.06, 1.08, 1.07, 1.09, 1.10, 1.11, 1.10, 1.09, 1.08, 1.07, 1.06, 1.05,  // 2024
            1.04, 1.03, 1.02, 1.01, 1.00, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93   // 2025
          ],
          borderColor: '#28a745',
          backgroundColor: 'rgba(40,167,69,0.1)',
          tension: 0.3
        }
      ]
    };

    /* --- Данные и конфигурация для графика фиатных валют --- */
    const fiatData = {
      labels: baseLabels,
      datasets: [
        {
          label: 'RUB/EUR',
          data: [
            90, 90.5, 91, 91.5, 92, 92.5, 93, 93.5, 94, 94.5, 95, 95.5,  // 2023
            96, 96.5, 97, 97.5, 98, 98.5, 99, 99.5, 100, 100.5, 101, 101.5,  // 2024
            102, 102.5, 103, 103.5, 104, 104.5, 105, 105.5, 106, 106.5, 107, 107.5   // 2025
          ],
          borderColor: '#6f42c1',
          backgroundColor: 'rgba(111,66,193,0.1)',
          tension: 0.3
        },
        {
          label: 'RUB/USD',
          data: [
            70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81,  // 2023
            82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,  // 2024
            94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105  // 2025
          ],
          borderColor: '#007bff',
          backgroundColor: 'rgba(0,123,255,0.1)',
          tension: 0.3
        },
        {
          label: 'AED',
          data: [
            3.67, 3.67, 3.68, 3.68, 3.69, 3.69, 3.70, 3.70, 3.71, 3.71, 3.72, 3.72,  // 2023
            3.73, 3.73, 3.74, 3.74, 3.75, 3.75, 3.76, 3.76, 3.77, 3.77, 3.78, 3.78,  // 2024
            3.79, 3.79, 3.80, 3.80, 3.81, 3.81, 3.82, 3.82, 3.83, 3.83, 3.84, 3.84   // 2025
          ],
          borderColor: '#ff5722',
          backgroundColor: 'rgba(255,87,34,0.1)',
          tension: 0.3
        },
        {
          label: 'CNY',
          data: [
            6.45, 6.46, 6.47, 6.48, 6.49, 6.50, 6.51, 6.52, 6.53, 6.54, 6.55, 6.56,  // 2023
            6.57, 6.58, 6.59, 6.60, 6.61, 6.62, 6.63, 6.64, 6.65, 6.66, 6.67, 6.68,  // 2024
            6.69, 6.70, 6.71, 6.72, 6.73, 6.74, 6.75, 6.76, 6.77, 6.78, 6.79, 6.80   // 2025
          ],
          borderColor: '#28a745',
          backgroundColor: 'rgba(40,167,69,0.1)',
          tension: 0.3
        }
      ]
    };

    // Инициализация графиков
    const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
    const cryptoChart = new Chart(cryptoCtx, {
      type: 'line',
      data: cryptoData,
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
            type: 'logarithmic',
            display: true,
            title: { display: true, text: 'Курс (USD)' },
            ticks: {
              callback: function(value) {
                return value;
              }
            }
          }
        }
      }
    });

    const fiatCtx = document.getElementById('fiatChart').getContext('2d');
    const fiatChart = new Chart(fiatCtx, {
      type: 'line',
      data: fiatData,
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
            display: true,
            title: { display: true, text: 'Курс' }
          }
        }
      }
    });

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
      cryptoChart.data.datasets.forEach((dataset, index) => {
        dataset.data = cryptoData.datasets[index].data.slice(-range);
      });
      cryptoChart.update();

      fiatChart.data.labels = newLabels;
      fiatChart.data.datasets.forEach((dataset, index) => {
        dataset.data = fiatData.datasets[index].data.slice(-range);
      });
      fiatChart.update();
    });
    </script>
// ... existing code ...
```
Я внес следующие изменения в `frontpage.html`:

1. Обновил селектор интервалов:
   - Добавил новые опции: "6 месяцев" и "3 года"
   - Установил "3 года" как значение по умолчанию
   - Убрал часовые и дневные интервалы, оставив только месячные и годовые

2. Добавил функцию генерации меток времени:
   - Теперь метки генерируются автоматически для периода с 2023 по 2025 год
   - Формат меток: "YYYY-MM"

3. Обновил данные для всех валют:
   - Добавил полные наборы данных за 36 месяцев (3 года)
   - Вернул AED (дирхам ОАЭ) в график фиатных валют
   - Структурировал данные по годам с комментариями

4. Улучшил конфигурацию графиков:
   - Добавил более информативные подписи осей
   - Улучшил отображение значений на логарифмической шкале
   - Оптимизировал отображение легенды

5. Заменил систему обновления данных:
   - Убрал автоматическое обновление каждые 5 минут
   - Добавил обработчик изменения интервала, который позволяет динамически менять период отображения данных
   - Реализовал корректное обрезание данных при изменении временного интервала

Теперь графики отображают более реалистичные данные за трехлетний период и позволяют пользователю выбирать различные временные интервалы для анализа. Хотите ли вы внести какие-либо дополнительные изменения в функциональность или отображение данных?
