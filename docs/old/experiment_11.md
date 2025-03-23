Below is a complete HTML mockup based on the previous version but now using a static sample of “actual” exchange‐rate–like data (for illustration only) covering the period from January 2023 through December 2025. In this example, we use monthly data (36 points) for each asset. In a real project you would replace these arrays with data fetched from an appropriate financial API. The cryptocurrency chart uses a logarithmic Y‑axis so that lower‐valued assets (like TON) are more easily visible, and the time‑range selector now actually slices the underlying data (showing 1 month, 6 months, 1 year, or the entire 3‑year span). 

Below is the complete code:

---

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>FIIT Финансовая Панель</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Google Fonts for a modern look -->
  <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" rel="stylesheet">

  <!-- Chart.js for demonstration graphs -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    /* Global Styles */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Roboto', sans-serif; background-color: #f4f7fa; color: #333; display: flex; min-height: 100vh; }
    a { text-decoration: none; color: inherit; }

    /* Sidebar */
    .sidebar {
      width: 250px;
      background-color: #767676; /* Lighter color as requested */
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
    .sidebar nav a:hover { background-color: #5a5a5a; }
    .sidebar h3 {
      margin-top: 20px;
      margin-bottom: 10px;
      font-size: 16px;
      text-transform: uppercase;
      color: #d1d1d1;
    }
    .sidebar .currencies div {
      margin-bottom: 6px;
      font-size: 14px;
    }

    /* Main Content */
    .main-content { flex-grow: 1; padding: 20px; overflow-y: auto; }

    /* Dashboard Header */
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
    .dashboard-header select {
      padding: 6px 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background-color: #fff;
    }

    /* Graph Container */
    .chart-container {
      background-color: #fff;
      border-radius: 6px;
      padding: 20px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
      margin-bottom: 20px;
    }
    .chart-container h4 { margin-bottom: 10px; }

    /* Responsive Design */
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
  <!-- Sidebar -->
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
      <div>AED</div>
    </div>
  </aside>

  <!-- Main Content -->
  <div class="main-content">
    <!-- Dashboard Header with time range selector -->
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
      </div>
    </div>

    <!-- Crypto Assets Chart (Logarithmic Scale) -->
    <div class="chart-container" id="cryptoAssets">
      <h4>Динамика криптовалют (BTC, ETH, TON)</h4>
      <canvas id="cryptoChart" height="140"></canvas>
      <small>Y-ось в логарифмическом масштабе.</small>
    </div>

    <!-- Fiat Assets Chart -->
    <div class="chart-container" id="fiatAssets">
      <h4>Динамика фиатных валют (RUB/EUR, RUB/USD, AED, CNY)</h4>
      <canvas id="fiatChart" height="140"></canvas>
    </div>
  </div>

  <!-- JavaScript: Data Arrays and Chart Initialization -->
  <script>
    // Generate monthly labels from Jan 2023 to Dec 2025 (36 months)
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

    // --- Crypto Assets Data (36 monthly points) ---
    const btcData = [
      21000, 22000, 23000, 22500, 22000, 21500, 21000, 21800, 22500, 23000, 24000, 23500,  // 2023
      25000, 26000, 25500, 26500, 27000, 27500, 28000, 28500, 29000, 29500, 30000, 31000,  // 2024
      32000, 31500, 31000, 30500, 31000, 31500, 32000, 32500, 33000, 33500, 34000, 34500   // 2025
    ];
    const ethData = [
      1600, 1650, 1700, 1680, 1660, 1640, 1620, 1630, 1650, 1670, 1700, 1690,  // 2023
      1720, 1750, 1740, 1760, 1780, 1800, 1820, 1840, 1850, 1870, 1900, 1920,  // 2024
      1950, 1940, 1930, 1920, 1910, 1900, 1890, 1880, 1870, 1860, 1850, 1840   // 2025
    ];
    const tonData = [
      1.00, 1.02, 1.05, 1.03, 1.01, 1.00, 0.98, 1.00, 1.02, 1.03, 1.05, 1.04,  // 2023
      1.06, 1.08, 1.07, 1.09, 1.10, 1.11, 1.10, 1.09, 1.08, 1.07, 1.06, 1.05,  // 2024
      1.04, 1.03, 1.02, 1.01, 1.00, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93   // 2025
    ];

    // --- Fiat Assets Data (36 monthly points) ---
    const rubEurData = [
      90, 90.5, 91, 91.5, 92, 92.5, 93, 93.5, 94, 94.5, 95, 95.5,  // 2023
      96, 96.5, 97, 97.5, 98, 98.5, 99, 99.5, 100, 100.5, 101, 101.5,  // 2024
      102, 102.5, 103, 103.5, 104, 104.5, 105, 105.5, 106, 106.5, 107, 107.5   // 2025
    ];
    const rubUsdData = [
      70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81,  // 2023
      82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,  // 2024
      94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105  // 2025
    ];
    const aedData = [
      3.67, 3.67, 3.68, 3.68, 3.69, 3.69, 3.70, 3.70, 3.71, 3.71, 3.72, 3.72,  // 2023
      3.73, 3.73, 3.74, 3.74, 3.75, 3.75, 3.76, 3.76, 3.77, 3.77, 3.78, 3.78,  // 2024
      3.79, 3.79, 3.80, 3.80, 3.81, 3.81, 3.82, 3.82, 3.83, 3.83, 3.84, 3.84   // 2025
    ];
    const cnyData = [
      6.45, 6.46, 6.47, 6.48, 6.49, 6.50, 6.51, 6.52, 6.53, 6.54, 6.55, 6.56,  // 2023
      6.57, 6.58, 6.59, 6.60, 6.61, 6.62, 6.63, 6.64, 6.65, 6.66, 6.67, 6.68,  // 2024
      6.69, 6.70, 6.71, 6.72, 6.73, 6.74, 6.75, 6.76, 6.77, 6.78, 6.79, 6.80   // 2025
    ];

    // Build base datasets for each chart
    // Crypto chart: BTC, ETH, TON
    const baseCryptoDatasets = [
      { label: 'BTC', data: btcData, borderColor: '#ff9800', backgroundColor: 'rgba(255,152,0,0.1)', tension: 0.3 },
      { label: 'ETH', data: ethData, borderColor: '#007bff', backgroundColor: 'rgba(0,123,255,0.1)', tension: 0.3 },
      { label: 'TON', data: tonData, borderColor: '#28a745', backgroundColor: 'rgba(40,167,69,0.1)', tension: 0.3 }
    ];

    // Fiat chart: RUB/EUR, RUB/USD, AED, CNY
    const baseFiatDatasets = [
      { label: 'RUB/EUR', data: rubEurData, borderColor: '#6f42c1', backgroundColor: 'rgba(111,66,193,0.1)', tension: 0.3 },
      { label: 'RUB/USD', data: rubUsdData, borderColor: '#007bff', backgroundColor: 'rgba(0,123,255,0.1)', tension: 0.3 },
      { label: 'AED', data: aedData, borderColor: '#ff5722', backgroundColor: 'rgba(255,87,34,0.1)', tension: 0.3 },
      { label: 'CNY', data: cnyData, borderColor: '#28a745', backgroundColor: 'rgba(40,167,69,0.1)', tension: 0.3 }
    ];

    // Create chart instances (using full data range by default: 3y, i.e. 36 points)
    const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
    const fiatCtx = document.getElementById('fiatChart').getContext('2d');

    const cryptoChart = new Chart(cryptoCtx, {
      type: 'line',
      data: {
        labels: baseLabels,
        datasets: baseCryptoDatasets.map(ds => Object.assign({}, ds, { data: ds.data.slice() }))
      },
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

    const fiatChart = new Chart(fiatCtx, {
      type: 'line',
      data: {
        labels: baseLabels,
        datasets: baseFiatDatasets.map(ds => Object.assign({}, ds, { data: ds.data.slice() }))
      },
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

    // Update both charts when interval selector changes
    document.getElementById('timeRange').addEventListener('change', (e) => {
      let range;
      switch(e.target.value) {
        case '1m': range = 1; break;
        case '6m': range = 6; break;
        case '1y': range = 12; break;
        case '3y': range = 36; break;
        default: range = 36;
      }
      
      // Slice baseLabels and each dataset’s data to the last "range" points:
      const newLabels = baseLabels.slice(-range);

      cryptoChart.data.labels = newLabels;
      cryptoChart.data.datasets.forEach((dataset, index) => {
        dataset.data = baseCryptoDatasets[index].data.slice(-range);
      });
      cryptoChart.update();

      fiatChart.data.labels = newLabels;
      fiatChart.data.datasets.forEach((dataset, index) => {
        dataset.data = baseFiatDatasets[index].data.slice(-range);
      });
      fiatChart.update();
    });
  </script>
</body>
</html>
```

---

### Explanation

1. **Data Arrays:**  
   The code includes sample arrays for three cryptocurrencies (BTC, ETH, TON) and four fiat pairs (RUB/EUR, RUB/USD, AED, CNY). Each array holds 36 monthly points spanning January 2023 to December 2025.

2. **Dynamic Labels:**  
   A helper function (`generateLabels`) creates an array of month labels in the format `"YYYY-MM"`. These serve as the x‑axis labels in both charts.

3. **Chart Initialization:**  
   Two Chart.js instances are created:
   - The crypto chart uses a logarithmic Y‑axis.
   - The fiat chart uses a linear Y‑axis.
  
4. **Working Interval Selector:**  
   The `<select>` element (with options for 1 month, 6 months, 1 year, and 3 years) triggers an update that slices each asset’s data (and the labels) to show only the most recent points for that interval.

5. **Actual Versus Sample Data:**  
   The numbers provided in these arrays are illustrative—when moving to production you would replace them with actual exchange rate values fetched (and updated) from your data source.

Feel free to adjust the sample arrays or logic as needed for your final implementation.