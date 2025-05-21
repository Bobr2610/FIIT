// Глобальные переменные
let allChartData = { labels: [], datasets: [] };
let combinedChartInstance = null;
// const exchangeratesFile = 'js/exchangerates.json'; // Эта строка должна быть удалена или закомментирована

// Описания валют
const currencyDescriptions = {
    BTC: 'Bitcoin - это децентрализованная цифровая валюта, не имеющая центрального банка или единого администратора.',
    ETH: 'Ethereum - это децентрализованная блокчейн-платформа с открытым исходным кодом и функциональностью смарт-контрактов.',
    TON: 'The Open Network (TON) - это быстрый, безопасный и масштабируемый блокчейн-проект.',
    USD: 'Доллар США - официальная валюта Соединенных Штатов и их территорий.',
    EUR: 'Евро - официальная валюта 19 из 27 стран-членов Европейского Союза.',
    CNY: 'Китайский юань (женьминьби) - официальная валюта Китайской Народной Республики.',
    AED: 'Дирхам ОАЭ - валюта Объединенных Арабских Эмиратов.'
    // Убедитесь, что ключи здесь соответствуют тем, что будут использоваться в графике (например, USD, EUR)
};

// Константа для настроек форматирования чисел (ОПРЕДЕЛЕНА ОДИН РАЗ)
const NUMBER_FORMAT_OPTIONS = {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
};

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

function generateLabels(currencyData, interval = 'all', dailyDataKey = null) {
    const labels = [];
    const allYears = Object.keys(currencyData).filter(k => k.match(/^\d{4}$/)).sort(); // Получаем все доступные годы

    if (dailyDataKey && currencyData[dailyDataKey] && interval === '1m') {
        const year = dailyDataKey.split('_')[1];
        const month = dailyDataKey.split('_')[2];
        const daysInMonth = currencyData[dailyDataKey].length;
        for (let i = 1; i <= daysInMonth; i++) {
            labels.push(`${year}-${month}-${i < 10 ? '0' + i : i}`);
        }
    } else {
        let yearsToProcess = allYears;
        if (interval === '1y') {
            yearsToProcess = allYears.slice(-1); // Последний год
        } else if (interval === '3y') {
            yearsToProcess = allYears.slice(-3); // Последние 3 года
        }
        // Для 'all' используем все доступные годы (yearsToProcess уже содержит их)

        yearsToProcess.forEach(year => {
            if (currencyData[year]) {
                for (let month = 1; month <= 12; month++) {
                    // Проверяем, есть ли данные за этот месяц в годовом массиве
                    if (currencyData[year][month - 1] !== undefined) {
                         labels.push(`${year}-${month < 10 ? '0' + month : month}`);
                    }
                }
            }
        });
    }
    return [...new Set(labels)].sort();
}

function combineYearlyData(currencyData, interval = 'all') {
    let combined = [];
    const allYears = Object.keys(currencyData).filter(k => k.match(/^\d{4}$/)).sort();

    if (interval === '1m') {
        // Если есть ключ daily_ для последнего месяца последнего года, используем его
        const lastYear = allYears.length > 0 ? allYears[allYears.length - 1] : null;
        if (lastYear) {
            const dailyKeysForLastYear = Object.keys(currencyData).filter(k => k.startsWith(`daily_${lastYear}_`)).sort();
            if (dailyKeysForLastYear.length > 0) {
                const lastMonthDailyKey = dailyKeysForLastYear[dailyKeysForLastYear.length -1];
                if(currencyData[lastMonthDailyKey]) return currencyData[lastMonthDailyKey];
            }
        }
        // Если нет дневных данных за последний месяц, возвращаем пустой массив или данные за последний год (как запасной вариант)
        // Для простоты пока вернем данные за последний год, если 1m запрошен, но нет daily
        if (lastYear && currencyData[lastYear]) return currencyData[lastYear];
        return [];
    }

    let yearsToProcess = allYears;
    if (interval === '1y') {
        yearsToProcess = allYears.slice(-1);
    } else if (interval === '3y') {
        yearsToProcess = allYears.slice(-3);
    }

    yearsToProcess.forEach(year => {
        if (currencyData[year]) {
            combined = combined.concat(currencyData[year]);
        }
    });
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

    // Убедимся, что все элементы в dataArray являются числами
    const numericData = dataArray.map(Number).filter(n => !isNaN(n));
    if (numericData.length === 0) return { average: '--', median: '--', outliers: '--' };

    const sortedData = [...numericData].sort((a, b) => a - b);
    const sum = sortedData.reduce((acc, val) => acc + val, 0);
    const average = sum / sortedData.length;
    const mid = Math.floor(sortedData.length / 2);
    const median = sortedData.length % 2 !== 0 ? sortedData[mid] : (sortedData[mid - 1] + sortedData[mid]) / 2;

    // Расчет выбросов с использованием IQR (Interquartile Range)
    const q1Index = Math.floor(sortedData.length / 4);
    const q3Index = Math.floor((3 * sortedData.length) / 4);
    const q1 = sortedData.length % 4 === 0 ? (sortedData[q1Index -1] + sortedData[q1Index]) / 2 : sortedData[q1Index];
    const q3 = sortedData.length % 4 === 0 ? (sortedData[q3Index -1] + sortedData[q3Index]) / 2 : sortedData[q3Index];
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;
    const outliers = sortedData.filter(val => val < lowerBound || val > upperBound).length;

    return {
        average: average.toFixed(2),
        median: median.toFixed(2),
        outliers: outliers
    };
}

// --- ФУНКЦИИ ДЛЯ РАБОТЫ С API И ОБНОВЛЕНИЯ ЦЕН ---

// Функция для получения CSRF токена (пример, вам нужно адаптировать)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function fetchRatesFromAPI() {
    // TODO: Implement token retrieval (access and refresh tokens)
    const accessToken = localStorage.getItem('accessToken'); // Пример: получение токена из localStorage
    const csrfToken = getCookie('csrftoken'); // Пример: получение CSRF токена

    const headers = {
        'Content-Type': 'application/json',
        // 'Authorization': `Bearer ${accessToken}`, // Раскомментируйте и адаптируйте, если используете Bearer токен
    };
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }

    try {
        const response = await fetch('/api/v1/rates/', { // Используем ваш API эндпоинт
            method: 'GET',
            headers: headers
        });
        if (!response.ok) {
            // TODO: Implement refresh token logic if applicable (e.g., on 401 Unauthorized)
            throw new Error(`HTTP error! status: ${response.status} while fetching /api/v1/rates/`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching rates from API:', error);
        throw error; // Перебрасываем ошибку для обработки выше
    }
}

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

function processChartData(rawData, interval = 'all') {
    const datasets = [];
    let allLabelsSet = new Set();

    const processCurrencyType = (currencyTypeData, type) => {
        for (const currencyCodeWithPair in currencyTypeData) {
            const baseCurrencyCode = currencyCodeWithPair.split('/')[0].toUpperCase();
            const currencyData = currencyTypeData[currencyCodeWithPair];
            let combinedData;
            let currentLabels;
            let dailyKeyForLabels = null;

            if (interval === '1m') {
                const allYears = Object.keys(currencyData).filter(k => k.match(/^\d{4}$/)).sort();
                const lastYear = allYears.length > 0 ? allYears[allYears.length - 1] : null;
                if (lastYear) {
                    const dailyKeysForLastYear = Object.keys(currencyData).filter(k => k.startsWith(`daily_${lastYear}_`)).sort();
                    if (dailyKeysForLastYear.length > 0) {
                        dailyKeyForLabels = dailyKeysForLastYear[dailyKeysForLastYear.length - 1];
                    }
                }
                combinedData = combineYearlyData(currencyData, interval);
                currentLabels = generateLabels(currencyData, interval, dailyKeyForLabels);
            } else {
                combinedData = combineYearlyData(currencyData, interval);
                currentLabels = generateLabels(currencyData, interval);
            }

            currentLabels.forEach(label => allLabelsSet.add(label));

            datasets.push({
                label: baseCurrencyCode,
                data: combinedData,
                // borderColor: getRandomColor(), // Цвет будет устанавливаться динамически
                // backgroundColor: getRandomColor(0.1), // Цвет будет устанавливаться динамически
                tension: 0.3,
                fill: false,
                hidden: true
            });
        }
    };

    if (rawData.crypto) processCurrencyType(rawData.crypto, 'crypto');
    if (rawData.fiat) processCurrencyType(rawData.fiat, 'fiat');

    const uniqueSortedLabels = [...allLabelsSet].sort();
    return { labels: uniqueSortedLabels, datasets };
}

function updateStatsDisplay(currency, stats) {
    console.log('Updating stats display for:', currency, 'with stats:', stats); 
    const statsPanel = document.querySelector('.currency-stats-panel');

    if (statsPanel) {
        // Убираем анимацию opacity и просто делаем панель видимой
        statsPanel.style.display = 'block'; // Убедимся, что панель отображается
        statsPanel.style.opacity = '1'; // Убедимся, что панель не прозрачная

        const selectedCurrencyNameEl = document.getElementById('selectedCurrencyName');
        const statDescriptionEl = document.getElementById('statDescription');
        const statAverageEl = document.getElementById('statAverage');
        const statMedianEl = document.getElementById('statMedian');
        const statOutliersEl = document.getElementById('statOutliers');

        if (selectedCurrencyNameEl) selectedCurrencyNameEl.textContent = `Статистика для: ${currency ? currency.toUpperCase() : 'Н/Д'}`;
        if (statDescriptionEl) statDescriptionEl.textContent = currencyDescriptions[currency ? currency.toUpperCase() : ''] || 'Описание для данной валюты отсутствует.';
        if (statAverageEl) statAverageEl.textContent = stats && stats.average !== undefined ? stats.average : '--';
        if (statMedianEl) statMedianEl.textContent = stats && stats.median !== undefined ? stats.median : '--';
        if (statOutliersEl) statOutliersEl.textContent = stats && stats.outliers !== undefined ? stats.outliers : '--';
        
        console.log('Stats panel updated and made visible.');
    } else {
        console.error('Currency stats panel not found!'); 
    }
}

function updateCombinedChartForSingleCurrency(selectedCurrency, interval) { // interval теперь обязательный параметр
    if (!combinedChartInstance || !allChartData.datasets) return;
    console.log(`Updating chart for ${selectedCurrency} with interval ${interval} and color ${currentChartColor}`);

    fetch(exchangeratesFile)
        .then(response => response.json())
        .then(rawData => {
            allChartData = processChartData(rawData, interval); // Передаем актуальный interval
            console.log(`Processed chart data for interval ${interval}:`, allChartData);

            const upperSelectedCurrency = selectedCurrency.toUpperCase();
            let datasetToShow = null;

            allChartData.datasets.forEach(d => {
                if (d.label.toUpperCase() === upperSelectedCurrency) {
                    d.hidden = false;
                    d.borderColor = currentChartColor; // Устанавливаем выбранный цвет
                    d.backgroundColor = currentChartColor.replace('rgb', 'rgba').replace(')', ', 0.1)'); // Для заливки
                    datasetToShow = d;
                } else {
                    d.hidden = true;
                }
            });

            if (datasetToShow) {
                combinedChartInstance.data.labels = allChartData.labels;
                combinedChartInstance.data.datasets = allChartData.datasets;
                combinedChartInstance.update();
                const stats = calculateStats(datasetToShow.data);
                console.log('Calling updateStatsDisplay from updateCombinedChartForSingleCurrency (dataset found)'); // Логирование
                updateStatsDisplay(selectedCurrency, stats); // Убедимся, что вызывается здесь
            } else {
                console.warn(`Dataset for ${selectedCurrency} not found after processing for interval ${interval}`);
                combinedChartInstance.data.labels = [];
                combinedChartInstance.data.datasets = [];
                combinedChartInstance.update();
                console.log('Calling updateStatsDisplay from updateCombinedChartForSingleCurrency (dataset NOT found)'); // Логирование
                updateStatsDisplay(selectedCurrency, { average: '--', median: '--', outliers: '--', description: 'Данные не найдены.' });
            }
        })
        .catch(error => {
            console.error(`Error fetching or processing data for interval ${interval}:`, error);
            const chartWrapper = document.querySelector('.chart-wrapper');
            if (chartWrapper) {
                chartWrapper.innerHTML = `<p style="color: red; text-align: center;">Не удалось загрузить данные для графика: ${error.message}. Проверьте консоль.</p>`;
            }
            console.log('Calling updateStatsDisplay from updateCombinedChartForSingleCurrency (catch block)'); // Логирование
            updateStatsDisplay(selectedCurrency, { average: 'Ошибка', median: 'Ошибка', outliers: 'Ошибка', description: 'Не удалось загрузить данные.' });
        });
}

async function initializeDashboard() {
    console.log('[initializeDashboard] Initializing...');
    const chartCanvas = document.getElementById('combinedChart');
    const timeRangeSelect = document.getElementById('timeRange'); // Объявляем здесь
    const colorPicker = document.getElementById('chartColorPicker'); // Объявляем здесь

    if (timeRangeSelect) {
        currentInterval = timeRangeSelect.value; // Initialize from dropdown
    }
    if (colorPicker) {
        currentChartColor = colorPicker.value; // Initialize from color picker
    }

    if (!chartCanvas) {
        console.error('Error: Chart canvas element (combinedChart) not found.');
        updateStatsDisplay('Ошибка', { average: '!', median: '!', outliers: '!', description: 'Элемент графика не найден.' });
        return;
    }

    try {
        const response = await fetch(exchangeratesFile); // exchangeratesFile is global from HTML
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} while fetching ${exchangeratesFile}`);
        }
        window.exchangeRatesData = await response.json(); // Store globally for easier access
        console.log('[initializeDashboard] Exchange rates data loaded:', window.exchangeRatesData);

        allChartData = processChartData(window.exchangeRatesData, currentInterval);
        console.log('[initializeDashboard] Processed chart data:', allChartData);

        if (!allChartData.labels || !allChartData.datasets || allChartData.datasets.length === 0) {
            console.error('[initializeDashboard] No data available to display on the chart after processing.');
            updateStatsDisplay('Нет данных', { average: '--', median: '--', outliers: '--', description: 'Нет данных для отображения на графике.' });
            // return; // Optional: stop if no data, or draw an empty chart
        }

        const ctx = chartCanvas.getContext('2d');
        if (combinedChartInstance) {
            combinedChartInstance.destroy();
        }

        combinedChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allChartData.labels,
                datasets: allChartData.datasets.map(ds => ({
                    ...ds,
                    hidden: true, // Initially hide all datasets
                    borderColor: currentChartColor, // Apply initial color
                    backgroundColor: currentChartColor.replace('rgb', 'rgba').replace(')', ', 0.1)') // Apply initial color with opacity
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false, 
                        type: 'logarithmic', 
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-color').trim(),
                            callback: function(value, index, values) {
                                // Показываем метки для 1, 2, 5 на каждом порядке величины
                                const logValue = Math.log10(value);
                                const remainder = logValue - Math.floor(logValue);
                                
                                // Проверяем, близко ли значение к 1, 2, 5 (с учетом погрешности для логарифмов)
                                const isOne = Math.abs(remainder) < 0.001 || Math.abs(remainder - 1) < 0.001;
                                const isTwo = Math.abs(remainder - Math.log10(2)) < 0.001;
                                const isFive = Math.abs(remainder - Math.log10(5)) < 0.001;

                                if (isOne || isTwo || isFive) {
                                    if (value >= 1000000) return (value / 1000000).toLocaleString(undefined, NUMBER_FORMAT_OPTIONS) + 'M';
                                    if (value >= 1000) return (value / 1000).toLocaleString(undefined, NUMBER_FORMAT_OPTIONS) + 'K';
                                    return value.toLocaleString(undefined, NUMBER_FORMAT_OPTIONS);
                                }
                                return ''; // Скрываем остальные метки
                            },
                            // Можно также попробовать увеличить максимальное количество тиков, если Chart.js это поддерживает для логарифмической шкалы
                            // maxTicksLimit: 15 // Например, но это может не сработать как ожидается с логарифмической шкалой и callback
                        },
                        grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-grid-color').trim() }
                    },
                    x: {
                        ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-color').trim() },
                        grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-grid-color').trim() }
                    }
                },
                plugins: {
                    legend: { 
                        display: false // Убедимся, что легенда отключена
                    },
                    tooltip: { mode: 'index', intersect: false }
                },
                animation: { duration: 500, easing: 'easeInOutQuart' }
            }
        });
        console.log('[initializeDashboard] Chart instance created.');

        // Determine initial currency to display
        const currencyButtons = document.querySelectorAll('.currency-selector-panel .currency-btn');
        let initialCurrencyCode = 'BTC'; // По умолчанию BTC

        if (currencyButtons.length > 0) {
            // Устанавливаем активное состояние для первой кнопки, если она есть
            const firstButton = currencyButtons[0];
            if (firstButton) {
                firstButton.classList.add('active');
                initialCurrencyCode = firstButton.getAttribute('data-currency');
            }
            
            // Можно добавить логику для выбора предпочтительной валюты, если BTC не первая
            // Например, найти кнопку BTC и сделать ее активной:
            const btcButton = Array.from(currencyButtons).find(btn => btn.getAttribute('data-currency') === 'BTC');
            if (btcButton) {
                currencyButtons.forEach(btn => btn.classList.remove('active')); // Сначала убираем active у всех
                btcButton.classList.add('active');
                initialCurrencyCode = 'BTC';
            } else if (firstButton) { // Если BTC нет, оставляем активной первую
                 currencyButtons.forEach(btn => btn.classList.remove('active'));
                 firstButton.classList.add('active');
                 initialCurrencyCode = firstButton.getAttribute('data-currency');
            }
        }
        console.log('[initializeDashboard] Initial currency code set to:', initialCurrencyCode);

        updateCombinedChartForSingleCurrency(initialCurrencyCode, currentInterval);

        // Event listeners for currency buttons
        currencyButtons.forEach(button => {
            button.addEventListener('click', () => {
                currencyButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                const selectedCurrency = button.getAttribute('data-currency');
                updateCombinedChartForSingleCurrency(selectedCurrency, currentInterval);
            });
        });

        // Обработчик для выпадающего списка интервалов
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (event) => {
                currentInterval = event.target.value;
                const activeButton = document.querySelector('.currency-selector-panel .currency-btn.active');
                const selectedCurrency = activeButton ? activeButton.getAttribute('data-currency') : initialCurrencyCode;
                updateCombinedChartForSingleCurrency(selectedCurrency, currentInterval);
            });
        }

        // Обработчик для выбора цвета
        if (colorPicker) {
            colorPicker.addEventListener('input', (event) => {
                currentChartColor = event.target.value;
                const activeButton = document.querySelector('.currency-selector-panel .currency-btn.active');
                const selectedCurrency = activeButton ? activeButton.getAttribute('data-currency') : initialCurrencyCode;
                updateCombinedChartForSingleCurrency(selectedCurrency, currentInterval);
            });
        }

        console.log('[initializeDashboard] Initialization complete.');

    } catch (error) {
        console.error('[initializeDashboard] Error during initialization:', error);
        const chartWrapper = document.querySelector('.chart-wrapper');
        if (chartWrapper) {
            chartWrapper.innerHTML = `<p style="color: red; text-align: center;">Не удалось инициализировать график: ${error.message}. Проверьте консоль.</p>`;
        }
        updateStatsDisplay('Ошибка', { average: '!', median: '!', outliers: '!', description: 'Ошибка инициализации графика.' });
    }
}

document.addEventListener('DOMContentLoaded', initializeDashboard);