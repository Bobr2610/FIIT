Below is the updated HTML mockup. In this version the "Криптовалюты" (crypto assets) chart has its Y-axis set to a logarithmic scale. This will enhance the visibility of smaller values while preserving a clear view of larger fluctuations. The rest of the page remains unchanged.

---

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>FIIT Финансовая Панель</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <!-- Google Fonts для современного стиля -->
  <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" rel="stylesheet">
  
  <!-- Chart.js для демонстрационных графиков -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  
  <style>
    /* Глобальные стили */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Roboto', sans-serif; background-color: #f4f7fa; color: #333; display: flex; min-height: 100vh; }
    a { text-decoration: none; color: inherit; }
    
    /* Сайдбар */
    .sidebar {
      width: 250px;
      background-color: #1f2633;
      color: #fff;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      padding: 20px;
    }
    .sidebar .logo {
      margin-bottom: 30px;
      text-align: center;
    }
    .sidebar .logo img {
      width: 150px;
      object-fit: contain;
    }
    .sidebar nav a {
      display: block;
      padding: 12px 20px;
      margin-bottom: 10px;
      border-radius: 4px;
      transition: background 0.3s ease;
    }
    .sidebar nav a:hover { background-color: #3a4563; }
    .sidebar h3 {
      margin-top: 20px;
      margin-bottom: 10px;
      font-size: 16px;
      text-transform: uppercase;
      color: #a1aab2;
    }
    
    /* Основной контент */
    .main-content { flex-grow: 1; padding: 20px; overflow-y: auto; }
    
    /* Хедер панели */
    .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    .dashboard-header .time-filter {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .dashboard-header select,
    .dashboard-header input {
      padding: 6px 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background-color: #fff;
    }
    
    /* Контейнер для графика */
    .chart-container {
      background-color: #fff;
      border-radius: 6px;
      padding: 20px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    .chart-container h4 { margin-bottom: 10px; }
    
    /* Портфель */
    .portfolio {
      background-color: #fff;
      border-radius: 6px;
      padding: 20px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .portfolio h4 { margin-bottom: 15px; }
    .portfolio .balance { font-size: 24px; margin-bottom: 15px; }
    
    /* Адаптивность */
    @media (max-width: 768px) {
      body { flex-direction: column; }
      .sidebar {
        width: 100%;
        padding: 10px;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
      }
      .sidebar nav { display: flex; gap: 10px; }
      .main-content { padding: 10px; }
    }
  </style>
</head>
<body>
  <!-- Сайдбар с логотипом и навигацией -->
  <aside class="sidebar">
    <div class="logo">
      <img src="https://raw.githubusercontent.com/Bobr2610/FIIT/main/Logo.png" alt="Логотип FIIT">
    </div>
    <nav>
      <a href="#dashboard">Панель</a>
      <a href="#cryptoAssets">Криптовалюты</a>
      <a href="#fiatAssets">Фиат</a>
      <a href="#portfolio">Портфель</a>
      <a href="#news">Новости</a>
      <a href="#alerts">Оповещения</a>
      <a href="#account">Аккаунт</a>
    </nav>
    
    <h3>Валюты</h3>
    <div class="currencies">
      <div>USD - Доллар США</div>
      <div>EUR - Евро</div>
      <div>CNY - Юань</div>
      <div>BTC - Биткоин</div>
      <div>ETH - Эфириум</div>
      <div>TON - TON</div>
      <div>RUB/EUR</div>
      <div>RUB/USD</div>
      <div>UAED</div>
    </div>
  </aside>
  
  <!-- Основной контент -->
  <div class="main-content">
    <!-- Хедер панели (фильтры и выбор темы) -->
    <div class="dashboard-header" id="dashboard">
      <h2>Обзор рынка</h2>
      <div class="time-filter">
        <label for="timeRange">Интервал:</label>
        <select id="timeRange">
          <option value="1h">1 час</option>
          <option value="1d">1 день</option>
          <option value="1m">1 месяц</option>
          <option value="1y">1 год</option>
        </select>
        <label for="colorScheme">Тема:</label>
        <select id="colorScheme">
          <option value="default">Стандартная</option>
          <option value="colorblind">Для дальтоников</option>
        </select>
      </div>
    </div>
    
    <!-- График криптоактивов с логарифмической Y-осью -->
    <div class="chart-container" id="cryptoAssets">
      <h4>Динамика криптовалют</h4>
      <canvas id="cryptoChart" height="140"></canvas>
      <small>Отображение изменений для BTC, ETH, TON и других основных криптовалют. Y-ось настроена в логарифмическом масштабе.</small>
    </div>
    
    <!-- График фиатных валют -->
    <div class="chart-container" id="fiatAssets">
      <h4>Динамика фиатных валют</h4>
      <canvas id="fiatChart" height="140"></canvas>
      <small>Отображение курсов для RUB/EUR, RUB/USD, UAED, CNY и других валют.</small>
    </div>
    
    <!-- Портфель пользователя -->
    <div class="portfolio" id="portfolio">
      <h4>Ваш портфель</h4>
      <div class="balance">Баланс: 10 000 у.е.</div>
      <table style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="text-align: left; border-bottom: 1px solid #ddd;">
            <th>Валюта</th>
            <th>Количество</th>
            <th>Текущий курс</th>
            <th>Общая стоимость</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>USD</td>
            <td>2000</td>
            <td>1.0</td>
            <td>2000</td>
          </tr>
          <tr>
            <td>BTC</td>
            <td>0.5</td>
            <td>20000</td>
            <td>10000</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Финансовые новости -->
    <div class="chart-container" id="news">
      <h4>Финансовые новости</h4>
      <ul style="list-style-type: none; padding-left: 0;">
        <li style="margin-bottom: 10px;">
          <strong>12:30</strong> — Рынок криптовалют демонстрирует повышенную волатильность: аналитики прогнозируют возможное снижение.
        </li>
        <li style="margin-bottom: 10px;">
          <strong>11:15</strong> — Евро укрепился на фоне свежих экономических данных. Эксперт поделился своими выводами.
        </li>
        <li style="margin-bottom: 10px;">
          <strong>10:00</strong> — Рубль стабилизируется по отношению к USD, а спрос на евро заметно растёт.
        </li>
      </ul>
    </div>
    
    <!-- Оповещения -->
    <div class="chart-container" id="alerts">
      <h4>Оповещения</h4>
      <p>
        Выберите валюту для отслеживания и получайте уведомления по электронной почте или Telegram, когда достигаются заданные пороговые значения.
      </p>
    </div>
    
    <!-- Управление аккаунтом -->
    <div class="chart-container" id="account">
      <h4>Управление аккаунтом</h4>
      <p>
        <strong>Вход / Регистрация</strong><br>
        <button>Войти</button> <button>Зарегистрироваться</button>
      </p>
    </div>
  </div>
  
  <!-- JavaScript для Chart.js и имитации обновления данных -->
  <script>
    // Временные метки (12 точек)
    const timeLabels = ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"];

    /* --- Данные и конфигурация для графика криптоактивов --- */
    const cryptoData = {
      labels: [...timeLabels],
      datasets: [
        {
          label: 'BTC',
          data: [20000, 20200, 19800, 19950, 20100, 20050, 20250, 20300, 20150, 20000, 19900, 20100],
          borderColor: '#ff9800',
          backgroundColor: 'rgba(255,152,0,0.1)',
          tension: 0.3
        },
        {
          label: 'ETH',
          data: [1500, 1520, 1485, 1500, 1510, 1505, 1525, 1530, 1500, 1490, 1500, 1510],
          borderColor: '#007bff',
          backgroundColor: 'rgba(0,123,255,0.1)',
          tension: 0.3
        },
        {
          label: 'TON',
          data: [2.00, 2.10, 1.90, 2.00, 2.05, 2.00, 2.10, 2.20, 2.00, 1.95, 2.00, 2.10],
          borderColor: '#28a745',
          backgroundColor: 'rgba(40,167,69,0.1)',
          tension: 0.3
        }
      ]
    };

    // Конфигурация для графика криптоактивов с логарифмической Y-осью
    const cryptoConfig = {
      type: 'line',
      data: cryptoData,
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { tooltip: { enabled: true }, legend: { position: 'bottom' } },
        scales: {
          x: {
            display: true,
            title: { display: true, text: 'Время' }
          },
          y: {
            type: 'logarithmic',
            display: true,
            title: { display: true, text: 'Курс' },
            ticks: {
              callback: function(value) {
                return Math.round(value * 100) / 100;
              }
            }
          }
        }
      }
    };

    /* --- Данные и конфигурация для графика фиатных валют --- */
    const fiatData = {
      labels: [...timeLabels],
      datasets: [
        {
          label: 'RUB/EUR',
          data: [90, 91, 90.5, 92, 91.5, 90, 92, 91, 90.8, 92, 91.2, 90.5],
          borderColor: '#6f42c1',
          backgroundColor: 'rgba(111,66,193,0.1)',
          tension: 0.3
        },
        {
          label: 'RUB/USD',
          data: [70, 70.5, 69.5, 70, 71, 70.2, 70.8, 71.2, 70, 69.8, 70.4, 70],
          borderColor: '#007bff',
          backgroundColor: 'rgba(0,123,255,0.1)',
          tension: 0.3
        },
        {
          label: 'UAED',
          data: [3.67, 3.68, 3.66, 3.67, 3.69, 3.67, 3.70, 3.68, 3.66, 3.67, 3.68, 3.69],
          borderColor: '#ff5722',
          backgroundColor: 'rgba(255,87,34,0.1)',
          tension: 0.3
        },
        {
          label: 'CNY',
          data: [6.45, 6.46, 6.44, 6.45, 6.47, 6.45, 6.48, 6.46, 6.44, 6.45, 6.46, 6.47],
          borderColor: '#28a745',
          backgroundColor: 'rgba(40,167,69,0.1)',
          tension: 0.3
        }
      ]
    };

    const fiatConfig = {
      type: 'line',
      data: fiatData,
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { tooltip: { enabled: true }, legend: { position: 'bottom' } },
        scales: {
          x: {
            display: true,
            title: { display: true, text: 'Время' }
          },
          y: {
            display: true,
            title: { display: true, text: 'Курс' }
          }
        }
      }
    };

    // Инициализация графиков
    const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
    const cryptoChart = new Chart(cryptoCtx, cryptoConfig);
    
    const fiatCtx = document.getElementById('fiatChart').getContext('2d');
    const fiatChart = new Chart(fiatCtx, fiatConfig);
    
    // Симуляция обновлений данных каждые 5 минут (300000 мс)
    setInterval(() => {
      const currentTime = new Date().toLocaleTimeString().slice(0,5);
      
      // Обновление меток времени для обоих графиков
      cryptoData.labels.push(currentTime);
      fiatData.labels.push(currentTime);
      
      // Обновление данных для криптовалют
      cryptoData.datasets.forEach(dataset => {
        const lastValue = parseFloat(dataset.data[dataset.data.length - 1]);
        const fluctuation = (Math.random() - 0.5) * 0.02 * lastValue;
        dataset.data.push((lastValue + fluctuation).toFixed(2));
      });
      
      // Обновление данных для фиатных валют
      fiatData.datasets.forEach(dataset => {
        const lastValue = parseFloat(dataset.data[dataset.data.length - 1]);
        const fluctuation = (Math.random() - 0.5) * 0.02 * lastValue;
        dataset.data.push((lastValue + fluctuation).toFixed(2));
      });
      
      // Ограничение длины массивов до 18 точек
      if (cryptoData.labels.length > 18) {
        cryptoData.labels.shift();
        cryptoData.datasets.forEach(dataset => dataset.data.shift());
      }
      if (fiatData.labels.length > 18) {
        fiatData.labels.shift();
        fiatData.datasets.forEach(dataset => dataset.data.shift());
      }
      
      cryptoChart.update();
      fiatChart.update();
    }, 300000); // 300000 мс = 5 минут
  </script>
</body>
</html>
```

---

### Объяснение изменений

- **Логарифмическая Y-ось для криптовалют:**  
  В конфигурации `cryptoConfig` для графика криптоактивов добавлен параметр `type: 'logarithmic'` для оси Y. Это позволяет маленьким значениям отображаться более детально.

- **Тики оси Y:**  
  Функция `callback` для тиков округляет значения для лучшего восприятия.

Эта модификация улучшает визуальное представление динамики криптовалютных курсов. Хотите ли вы добавить дополнительные настройки для отображения мелких деталей на графике или провести оптимизацию по другим параметрам?