// Глобальные переменные
let allChartData = { labels: [], datasets: [] };
let combinedChartInstance = null;
// const exchangeratesFile = 'js/exchangerates.json'; // Удаляем или комментируем эту строку

// Описания валют
const currencyDescriptions = {
    BTC: 'Bitcoin - это децентрализованная цифровая валюта, не имеющая центрального банка или единого администратора.',
    ETH: 'Ethereum - это децентрализованная блокчейн-платформа с открытым исходным кодом и функциональностью смарт-контрактов.',
    TON: 'The Open Network (TON) - это быстрый, безопасный и масштабируемый блокчейн-проект.',
    USD: 'Доллар США - официальная валюта Соединенных Штатов и их территорий.',
    EUR: 'Евро - официальная валюта 19 из 27 стран-членов Европейского Союза.',
    CNY: 'Китайский юань (женьминьби) - официальная валюта Китайской Народной Республики.',
    AED: 'Дирхам ОАЭ - валюта Объединенных Арабских Эмиратов.'
};

// Константа для настроек форматирования чисел (ОПРЕДЕЛЕНА ОДИН РАЗ)
const NUMBER_FORMAT_OPTIONS = {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
};

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

function generateLabels(yearlyData, dailyDataKey) {
    const labels = [];
    if (dailyDataKey && yearlyData[dailyDataKey]) { 
        const year = dailyDataKey.split('_')[1];
        const month = dailyDataKey.split('_')[2];
        const daysInMonth = yearlyData[dailyDataKey].length; 
        for (let i = 1; i <= daysInMonth; i++) {
            labels.push(`${year}-${month}-${i < 10 ? '0' + i : i}`);
        }
    } else { 
        const years = ['2023', '2024', '2025'].filter(year => yearlyData[year] && yearlyData[year].length > 0);
        years.forEach(year => {
            for (let month = 1; month <= 12; month++) {
                if (yearlyData[year] && yearlyData[year][month -1] !== undefined) { // Check if yearlyData[year] exists
                     labels.push(`${year}-${month < 10 ? '0' + month : month}`);
                }
            }
        });
    }
    return [...new Set(labels)].sort(); 
}

function combineYearlyData(currencyData) {
    let combined = [];
    if (currencyData && currencyData['2023']) combined = combined.concat(currencyData['2023']);
    if (currencyData && currencyData['2024']) combined = combined.concat(currencyData['2024']);
    if (currencyData && currencyData['2025']) combined = combined.concat(currencyData['2025']);
    // If data is directly an array (e.g. daily data for 1m interval)
    if(Array.isArray(currencyData)) return currencyData;
    return combined;
}

function getRandomColor(alpha = 1) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r},${g},${b},${alpha})`;
}

function calculateStats(dataArray) {
    if (!dataArray || dataArray.length === 0) return { average: '--', median: '--', outliers: '--' };
    const sortedData = [...dataArray].sort((a, b) => a - b);
    const sum = sortedData.reduce((acc, val) => acc + val, 0);
    const average = sum / sortedData.length;
    const mid = Math.floor(sortedData.length / 2);
    const median = sortedData.length % 2 !== 0 ? sortedData[mid] : (sortedData[mid - 1] + sortedData[mid]) / 2;
    // A more robust outlier detection might be needed, this is a simple example
    const outliers = sortedData.filter(val => val > average * 2 || val < average / 2).length;
    return {
        average: average.toFixed(2),
        median: median.toFixed(2),
        outliers: outliers
    };
}

// --- ФУНКЦИИ ДЛЯ РАБОТЫ С API И ОБНОВЛЕНИЯ ЦЕН ---

async function getBTCPriceFromBinance() {
  try {
    const btcUsdtResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
    const btcUsdtData = await btcUsdtResponse.json();
    const btcUsdtPrice = parseFloat(btcUsdtData.price);
    const usdtRubResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB');
    const usdtRubData = await usdtRubResponse.json();
    const usdtRubPrice = parseFloat(usdtRubData.price);
    return btcUsdtPrice * usdtRubPrice;
  } catch (error) {
    console.error('Ошибка при получении курса BTC:', error);
    return null;
  }
}

async function getETHPriceFromBinance() {
  try {
    const ethRubResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=ETHRUB');
    const ethRubData = await ethRubResponse.json();
    return parseFloat(ethRubData.price);
  } catch (error) {
    console.error('Ошибка при получении курса ETH:', error);
    return null;
  }
}

async function getTONPriceFromBinance() {
  try {
    const tonUsdtResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT');
    const tonUsdtData = await tonUsdtResponse.json();
    const tonUsdtPrice = parseFloat(tonUsdtData.price);
    const usdtRubResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB');
    const usdtRubData = await usdtRubResponse.json();
    const usdtRubPrice = parseFloat(usdtRubData.price);
    return tonUsdtPrice * usdtRubPrice;
  } catch (error) {
    console.error('Ошибка при получении курса TON:', error);
    return null;
  }
}

async function getFiatPricesFromMOEX() {
  try {
    const response = await fetch('https://iss.moex.com/iss/engines/currency/markets/selt/securities.json');
    const data = await response.json();
    const prices = {};
    const securities = data.securities.data;
    const columns = data.securities.columns;
    const secIdIndex = columns.indexOf('SECID');
    const prevPriceIndex = columns.indexOf('PREVPRICE');
    securities.forEach(security => {
      const secId = security[secIdIndex];
      const price = parseFloat(security[prevPriceIndex]);
      if (security[columns.indexOf('STATUS')] === 'A' && !isNaN(price)) {
        if (secId === 'USD000UTSTOM') prices.USD = price;
        else if (secId === 'EUR_RUB__TOM') prices.EUR = price;
        else if (secId === 'CNYRUB_TOM') prices.CNY = price;
        else if (secId === 'AEDRUB_TOD') prices.AED = price;
      }
    });
    return prices;
  } catch (error) {
    console.error('Ошибка при получении курсов фиатных валют:', error);
    return null;
  }
}

function adjustPriceFontSize() {
  const priceElements = document.querySelectorAll('.asset-item .price');
  priceElements.forEach(priceElement => {
    const parentWidth = priceElement.parentElement.offsetWidth;
    const iconWidth = priceElement.parentElement.querySelector('i').offsetWidth;
    const symbolWidth = priceElement.parentElement.querySelector('span:not(.price)').offsetWidth;
    const padding = 32; 
    const gap = 8; 
    const availableWidth = parentWidth - iconWidth - symbolWidth - padding - gap;
    let fontSize = 14; 
    priceElement.style.fontSize = `${fontSize}px`; // Reset to default before checking
    while (priceElement.scrollWidth > availableWidth && fontSize > 10) {
      fontSize--;
      priceElement.style.fontSize = `${fontSize}px`;
    }
  });
}

function formatPrice(price) { // ОДНА ВЕРСИЯ
  if (price === undefined || price === null) {
    return '— ₽';
  }
  return `${price.toLocaleString('ru-RU', NUMBER_FORMAT_OPTIONS)} ₽`;
}

async function updateAllPrices() { // ОДНА ВЕРСИЯ
  const refreshBtn = document.querySelector('.refresh-btn');
  const refreshIcon = refreshBtn ? refreshBtn.querySelector('i') : null;
  if (refreshIcon) refreshIcon.style.animation = 'spin 1s linear infinite';
  
  try {
    const [btcPrice, ethPrice, tonPrice, fiatPrices] = await Promise.all([
      getBTCPriceFromBinance(),
      getETHPriceFromBinance(),
      getTONPriceFromBinance(),
      getFiatPricesFromMOEX()
    ]);
    const priceElements = document.querySelectorAll('.asset-item .price');
    priceElements.forEach(element => {
      element.style.color = 'var(--accent-primary)';
      setTimeout(() => {
        element.style.color = 'var(--text-secondary)';
      }, 500);
    });
    const prices = [btcPrice, ethPrice, tonPrice, fiatPrices?.USD, fiatPrices?.EUR, fiatPrices?.CNY, fiatPrices?.AED];
    priceElements.forEach((element, index) => {
      if (prices[index] !== undefined) { // Ensure price exists before formatting
        element.textContent = formatPrice(prices[index]);
      }
    });
    adjustPriceFontSize();
  } catch (error) {
    console.error('Ошибка при обновлении цен:', error);
  } finally {
    if (refreshIcon) refreshIcon.style.animation = '';
  }
}

// --- ОСНОВНАЯ ЛОГИКА ДЭШБОРДА ---

function processChartData(rawData) {
    const datasets = [];
    let allLabelsSet = new Set(); // Use a Set for unique labels initially

    const processCurrencyType = (currencyTypeData, type) => {
        for (const currencyCode in currencyTypeData) {
            const currencyData = currencyTypeData[currencyCode];
            let combinedData;
            let currentLabels;

            // Check for daily data (e.g., 'daily_2025_01')
            const dailyKey = Object.keys(currencyData).find(k => k.startsWith('daily_'));
            if (dailyKey) {
                combinedData = currencyData[dailyKey];
                currentLabels = generateLabels({ [dailyKey]: currencyData[dailyKey] }, dailyKey);
            } else {
                combinedData = combineYearlyData(currencyData);
                currentLabels = generateLabels(currencyData); 
            }
            
            currentLabels.forEach(label => allLabelsSet.add(label));

            datasets.push({
                label: currencyCode.toUpperCase(), // Standardize to uppercase
                data: combinedData,
                borderColor: getRandomColor(), 
                backgroundColor: getRandomColor(0.1),
                tension: 0.3,
                fill: false, 
                hidden: true // Initially hide all datasets
            });
        }
    };

    if (rawData.crypto) processCurrencyType(rawData.crypto, 'crypto');
    if (rawData.fiat) processCurrencyType(rawData.fiat, 'fiat');

    const uniqueSortedLabels = [...allLabelsSet].sort();
    return { labels: uniqueSortedLabels, datasets };
}

function updateStatsDisplay(currency, stats) {
    const statsPanel = document.querySelector('.currency-stats-panel');
    if(statsPanel) statsPanel.style.opacity = 0; 
    setTimeout(() => {
        document.getElementById('selectedCurrencyName').textContent = `Статистика для: ${currency.toUpperCase()}`;
        document.getElementById('statDescription').textContent = currencyDescriptions[currency.toUpperCase()] || 'Описание для данной валюты отсутствует.';
        document.getElementById('statAverage').textContent = stats.average;
        document.getElementById('statMedian').textContent = stats.median;
        document.getElementById('statOutliers').textContent = stats.outliers;
        if(statsPanel) statsPanel.style.opacity = 1; 
    }, 300); 
}

function updateCombinedChartForSingleCurrency(selectedCurrency) {
    if (!combinedChartInstance || !allChartData.datasets) return;

    const upperSelectedCurrency = selectedCurrency.toUpperCase();
    let datasetToShow = null;

    allChartData.datasets.forEach(d => {
        if (d.label.toUpperCase() === upperSelectedCurrency) {
            d.hidden = false;
            datasetToShow = d;
        } else {
            d.hidden = true;
        }
    });

    if (datasetToShow) {
        combinedChartInstance.data.datasets = allChartData.datasets; // Pass all, hidden flags will manage visibility
        combinedChartInstance.update();
        const stats = calculateStats(datasetToShow.data);
        updateStatsDisplay(selectedCurrency, stats);
    } else {
        // If no specific dataset found, maybe clear the chart or show a message
        combinedChartInstance.data.datasets = [];
        combinedChartInstance.update();
        updateStatsDisplay(selectedCurrency, { average: '--', median: '--', outliers: '--', description: 'Данные не найдены.' });
    }
}

async function initializeDashboard() {
    console.log("Initializing dashboard..."); // Отладка
    try {
        // Initialize UI elements from scripts.js if they exist
        if (typeof initThemeSwitcher === 'function') initThemeSwitcher();
        if (typeof initDateTime === 'function') initDateTime();
        if (typeof initNotificationToggle === 'function') initNotificationToggle();

        console.log("Fetching data from:", exchangeratesFile); // Отладка - проверяем путь к файлу
        const response = await fetch(exchangeratesFile); // Используем глобальную переменную, установленную в HTML
        if (!response.ok) {
            console.error(`HTTP error! status: ${response.status} while fetching ${exchangeratesFile}`);
            throw new Error(`HTTP error! status: ${response.status} while fetching ${exchangeratesFile}`);
        }
        const rawData = await response.json();
        console.log("Raw data fetched:", rawData); // Отладка - смотрим сырые данные

        allChartData = processChartData(rawData);
        console.log("Processed chart data:", allChartData); // Отладка - смотрим обработанные данные

        const ctx = document.getElementById('combinedChart').getContext('2d');
        if (!ctx) {
            console.error("Canvas context 'combinedChart' not found!");
            throw new Error("Canvas context 'combinedChart' not found!");
        }
        if (combinedChartInstance) combinedChartInstance.destroy();

        const initialCurrencyCode = allChartData.datasets.length > 0 ? allChartData.datasets[0].label : 'BTC';
        console.log("Initial currency code:", initialCurrencyCode); // Отладка
        
        allChartData.datasets.forEach(ds => {
            ds.hidden = ds.label.toUpperCase() !== initialCurrencyCode.toUpperCase();
        });

        combinedChartInstance = new Chart(ctx, {
            type: 'line',
            data: { 
                labels: allChartData.labels,
                datasets: allChartData.datasets
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                scales: { 
                    y: { 
                        type: 'logarithmic', 
                        ticks: { callback: value => Number(value.toString()).toLocaleString() } 
                    },
                    x: { 
                        ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 15 }
                    }
                },
                plugins: { 
                    legend: { 
                        display: true, 
                        position: 'top',
                        labels: {
                            filter: (legendItem, chartData) => {
                                const dataset = chartData.datasets[legendItem.datasetIndex];
                                return !dataset.hidden;
                            }
                        }
                    }, 
                    tooltip: { 
                        mode: 'index', 
                        intersect: false, 
                        callbacks: { 
                           label: context => `${context.dataset.label || ''}: ${context.parsed.y !== null ? Number(context.parsed.y.toString()).toLocaleString() : ''}` 
                        }
                    }
                } 
            }
        });
        console.log("Chart instance created:", combinedChartInstance); // Отладка

        const initialDataset = allChartData.datasets.find(d => d.label.toUpperCase() === initialCurrencyCode.toUpperCase());
        if (initialDataset) {
            console.log("Initial dataset for stats:", initialDataset); // Отладка
            updateStatsDisplay(initialDataset.label, calculateStats(initialDataset.data));
            const activeButton = document.querySelector(`.currency-btn[data-currency="${initialDataset.label.toUpperCase()}"]`);
            if (activeButton) activeButton.classList.add('active');
        } else {
            console.warn("Initial dataset not found for stats display."); // Отладка
            updateStatsDisplay('--', { average: '--', median: '--', outliers: '--' });
        }

        document.querySelectorAll('.currency-btn').forEach(button => {
            button.addEventListener('click', () => {
                const selectedCurrency = button.dataset.currency;
                console.log("Currency button clicked:", selectedCurrency); // Отладка
                updateCombinedChartForSingleCurrency(selectedCurrency);
                document.querySelectorAll('.currency-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });

        const buyButton = document.getElementById('buyButton');
        const sellButton = document.getElementById('sellButton');
        if(buyButton) buyButton.addEventListener('click', () => {
            const activeCurrency = document.querySelector('.currency-btn.active')?.dataset.currency || 'валюты';
            alert(`Покупка ${activeCurrency.toUpperCase()} (в разработке)`);
        });
        if(sellButton) sellButton.addEventListener('click', () => {
            const activeCurrency = document.querySelector('.currency-btn.active')?.dataset.currency || 'валюты';
            alert(`Продажа ${activeCurrency.toUpperCase()} (в разработке)`);
        });
        console.log("Dashboard initialized successfully."); // Отладка
        
    } catch (error) {
        console.error("Error initializing dashboard:", error);
        const chartContainer = document.getElementById('combinedChart')?.parentElement;
        if (chartContainer) chartContainer.innerHTML = `<p style="color:var(--text-error, red); text-align:center; padding: 20px;">Не удалось загрузить данные для графика: ${error.message}</p>`;
        updateStatsDisplay('Ошибка', { average: 'N/A', median: 'N/A', outliers: 'N/A', description: 'Не удалось загрузить данные.' });
    }
}

// --- ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ ---

document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    updateAllPrices(); // Первоначальное обновление цен в шапке
    setInterval(updateAllPrices, 30000); // Периодическое обновление цен
});

// Обработчик изменения размера окна для подстройки шрифта цен
window.addEventListener('resize', adjustPriceFontSize);

// Обработчик для кнопки обновления цен
const refreshButton = document.querySelector('.refresh-btn');
if (refreshButton) {
    refreshButton.addEventListener('click', updateAllPrices);
}