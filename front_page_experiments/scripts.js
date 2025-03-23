/**
 * Генерация меток времени для графиков
 * @param {Date} start - Начальная дата
 * @param {number} count - Количество меток
 * @param {boolean} isDaily - Флаг для ежедневных меток
 * @returns {string[]} Массив меток времени
 * 
 * Функция создает метки времени в формате YYYY-MM-DD для графиков.
 * Поддерживает как месячные, так и ежедневные метки.
 */
function generateLabels(start, count, isDaily = false) {
  const labels = [];
  let current = new Date(start);
  
  if (isDaily) {
    // Генерация ежедневных меток для января 2025
    for (let i = 1; i <= 31; i++) {
      labels.push('2025-01-' + (i < 10 ? '0' + i : i));
    }
  } else {
    // Генерация месячных меток
    for (let i = 0; i < count; i++) {
      const month = current.getMonth() + 1;
      const year = current.getFullYear();
      labels.push(year + '-' + (month < 10 ? '0' + month : month));
      current.setMonth(current.getMonth() + 1);
    }
  }
  return labels;
}

/**
 * Объединение данных по годам в единый массив
 * @param {Object} yearlyData - Объект с данными по годам
 * @returns {number[]} Объединенный массив данных
 * 
 * Функция объединяет массивы данных за 2023, 2024 и 2025 годы
 * в один последовательный массив для построения графика.
 */
function combineYearlyData(yearlyData) {
  return [...yearlyData["2023"], ...yearlyData["2024"], ...yearlyData["2025"]];
}

/**
 * Получение данных в зависимости от выбранного интервала
 * @param {Object} data - Объект с данными
 * @param {string} interval - Выбранный интервал
 * @returns {number[]} Массив данных для графика
 * 
 * Функция возвращает соответствующий набор данных в зависимости
 * от выбранного временного интервала (1 месяц, 6 месяцев, 1 год, 3 года).
 */
function getDataForInterval(data, interval) {
  if (interval === '1m') {
    // Для месячного интервала используем ежедневные данные
    return data.daily_2025_01 || [];
  }
  // Для остальных интервалов объединяем годовые данные
  return combineYearlyData(data);
}

/**
 * Создание конфигурации для графика Chart.js
 * @param {string} type - Тип графика
 * @param {Object} data - Данные для графика
 * @param {Object} options - Дополнительные опции
 * @returns {Object} Конфигурация графика
 * 
 * Функция создает конфигурацию для графика с настройками:
 * - Адаптивность
 * - Интерактивность
 * - Подсказки
 * - Легенда
 * - Настройки осей
 */
function createChartConfig(type, data, options = {}) {
  // Получаем текущие CSS переменные для стилей
  const getComputedStyle = window.getComputedStyle(document.documentElement);
  
  return {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: data.datasets.map(dataset => {
        // Получаем ключ валюты для доступа к CSS переменным
        const currencyKey = dataset.label.split('/')[0].toLowerCase();
        
        // Получаем цвета из CSS переменных
        const color = getComputedStyle.getPropertyValue(`--chart-${currencyKey}-color`).trim();
        const bgColor = color.replace(')', `, ${getComputedStyle.getPropertyValue('--chart-bg-opacity').trim()})`);
        
        // Получаем стили точек и линий из CSS переменных
        const pointStyle = getComputedStyle.getPropertyValue(`--chart-${currencyKey}-point-style`).trim().replace(/['"]/g, '');
        const borderDash = getComputedStyle.getPropertyValue(`--chart-${currencyKey}-border-dash`).trim();
        
        return {
          ...dataset,
          borderColor: color,
          backgroundColor: bgColor,
          // Получаем размеры и стили из CSS переменных
          borderWidth: parseInt(getComputedStyle.getPropertyValue('--chart-line-width').trim()),
          pointRadius: parseInt(getComputedStyle.getPropertyValue('--chart-point-radius').trim()),
          pointHoverRadius: parseInt(getComputedStyle.getPropertyValue('--chart-point-hover-radius').trim()),
          pointBorderWidth: parseInt(getComputedStyle.getPropertyValue('--chart-point-border-width').trim()),
          pointHoverBorderWidth: parseInt(getComputedStyle.getPropertyValue('--chart-point-hover-border-width').trim()),
          pointStyle: pointStyle,
          borderDash: borderDash === '[]' ? [] : JSON.parse(borderDash),
          tension: parseFloat(getComputedStyle.getPropertyValue('--chart-line-tension').trim())
        };
      })
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        tooltip: { enabled: true },
        legend: { position: 'bottom' }
      },
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
      }
    }
  };
}

/**
 * Получение курса BTC с Binance
 * @returns {Promise<number>} Курс BTC в рублях
 */
async function getBTCPriceFromBinance() {
  try {
    // Получаем курс BTC/USDT
    const btcUsdtResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
    const btcUsdtData = await btcUsdtResponse.json();
    const btcUsdtPrice = parseFloat(btcUsdtData.price);

    // Получаем курс USDT/RUB
    const usdtRubResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB');
    const usdtRubData = await usdtRubResponse.json();
    const usdtRubPrice = parseFloat(usdtRubData.price);

    // Рассчитываем курс BTC в рублях
    const btcRubPrice = btcUsdtPrice * usdtRubPrice;
    return btcRubPrice;
  } catch (error) {
    console.error('Ошибка при получении курса BTC:', error);
    return null;
  }
}

/**
 * Получение курса ETH с Binance
 * @returns {Promise<number>} Курс ETH в рублях
 */
async function getETHPriceFromBinance() {
  try {
    // Получаем курс ETH/USDT
    const ethRubResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=ETHRUB');
    const ethRubData = await ethRubResponse.json();
    const ethRubPrice = parseFloat(ethRubData.price);

    return ethRubPrice;
  } catch (error) {
    console.error('Ошибка при получении курса ETH:', error);
    return null;
  }
}

/**
 * Получение текущего курса TON (The Open Network) с биржи Binance
 * Функция делает два запроса к API Binance:
 * 1. Получает курс TON/USDT (TON к USDT)
 * 2. Получает курс USDT/RUB (USDT к рублю)
 * Затем вычисляет итоговый курс TON в рублях путем перемножения этих значений
 * 
 * @returns {Promise<number|null>} Возвращает курс TON в рублях или null в случае ошибки
 */
async function getTONPriceFromBinance() {
  try {
    // Делаем запрос к API Binance для получения курса TON/USDT
    // Используем endpoint /api/v3/ticker/price с параметром symbol=TONUSDT
    const tonUsdtResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT');
    const tonUsdtData = await tonUsdtResponse.json();
    // Преобразуем строковое значение цены в число с плавающей точкой
    const tonUsdtPrice = parseFloat(tonUsdtData.price);

    // Делаем запрос к API Binance для получения курса USDT/RUB
    // Используем тот же endpoint с параметром symbol=USDTRUB
    const usdtRubResponse = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB');
    const usdtRubData = await usdtRubResponse.json();
    // Преобразуем строковое значение цены в число с плавающей точкой
    const usdtRubPrice = parseFloat(usdtRubData.price);

    // Вычисляем итоговый курс TON в рублях путем умножения
    // курса TON/USDT на курс USDT/RUB
    const tonRubPrice = tonUsdtPrice * usdtRubPrice;
    return tonRubPrice;
  } catch (error) {
    // В случае любой ошибки (сетевой, парсинга и т.д.)
    // логируем её в консоль и возвращаем null
    console.error('Ошибка при получении курса TON:', error);
    return null;
  }
}

/**
 * Получение курсов фиатных валют с MOEX
 * @returns {Promise<Object>} Курсы валют в рублях
 */
async function getFiatPricesFromMOEX() {
  try {
    // Делаем запрос к API Московской биржи для получения данных по валютным инструментам
    // Используем endpoint /iss/engines/currency/markets/selt/securities.json который возвращает список всех торгуемых валютных пар
    const response = await fetch('https://iss.moex.com/iss/engines/currency/markets/selt/securities.json');
    const data = await response.json();
    
    // Создаем пустой объект для хранения курсов валют
    const prices = {};
    // Получаем массив данных по ценным бумагам из ответа API
    const securities = data.securities.data;
    // Получаем массив названий колонок для определения индексов нужных полей
    const columns = data.securities.columns;
    
    // Находим индексы необходимых колонок в массиве columns:
    // SECID - идентификатор инструмента (например, USD000UTSTOM для доллара)
    // PREVPRICE - цена закрытия предыдущего дня
    // BOARDID - идентификатор режима торгов
    const secIdIndex = columns.indexOf('SECID');
    const prevPriceIndex = columns.indexOf('PREVPRICE');
    const boardIdIndex = columns.indexOf('BOARDID');
    
    // Перебираем все валютные инструменты
    securities.forEach(security => {
      // Получаем значения нужных полей для текущего инструмента
      const secId = security[secIdIndex];
      const boardId = security[boardIdIndex];
      const price = parseFloat(security[prevPriceIndex]);
      
      // Проверяем что инструмент активен (STATUS='A') и цена является числом
      if (security[columns.indexOf('STATUS')] === 'A' && !isNaN(price)) {
        // Для каждой валюты используем соответствующий инструмент расчетами tomorrow (TOM):
        // USD000UTSTOM - доллар США
        if (secId === 'USD000UTSTOM') {
          prices.USD = price;
        }
        // EUR_RUB__TOM - евро 
        else if (secId === 'EUR_RUB__TOM') {
          prices.EUR = price;
        }
        // CNYRUB_TOM - китайский юань
        else if (secId === 'CNYRUB_TOM') {
          prices.CNY = price;
        }
        // AEDRUB_TOM - дирхам ОАЭ
        else if (secId === 'AEDRUB_TOM') {
          prices.AED = price;
        }
      }
    });
    
    // Проверяем наличие всех необходимых курсов
    const requiredCurrencies = ['USD', 'EUR', 'CNY', 'AED'];
    const missingCurrencies = requiredCurrencies.filter(currency => !prices[currency]);
    
    if (missingCurrencies.length > 0) {
      console.warn('Не удалось получить курсы для следующих валют:', missingCurrencies);
    }
    
    return prices;
  } catch (error) {
    console.error('Ошибка при получении курсов фиатных валют:', error);
    return null;
  }
}

// Функция для подстройки размера шрифта цены
/**
 * Подстраивает размер шрифта цены под доступное пространство
 * 
 * Функция находит все элементы с ценами и для каждого:
 * 1. Вычисляет доступную ширину с учетом иконки, символа валюты и отступов
 * 2. Начиная с базового размера шрифта 14px, уменьшает его пока текст не поместится
 * 3. Минимальный размер шрифта - 10px
 * 
 * @returns {void}
 */
function adjustPriceFontSize() {
  const priceElements = document.querySelectorAll('.asset-item .price');
  
  priceElements.forEach(priceElement => {
    const parentWidth = priceElement.parentElement.offsetWidth;
    const iconWidth = priceElement.parentElement.querySelector('i').offsetWidth;
    const symbolWidth = priceElement.parentElement.querySelector('span:not(.price)').offsetWidth;
    const padding = 32; // Учитываем padding родителя
    const gap = 8; // Учитываем gap между элементами
    
    // Вычисляем доступную ширину для цены
    const availableWidth = parentWidth - iconWidth - symbolWidth - padding - gap;
    
    // Начинаем с базового размера шрифта
    let fontSize = 14; // var(--font-size-sm)
    
    // Проверяем, помещается ли текст
    while (priceElement.scrollWidth > availableWidth && fontSize > 10) {
      fontSize--;
      priceElement.style.fontSize = `${fontSize}px`;
    }
  });
}

// Константа для настроек форматирования чисел
const NUMBER_FORMAT_OPTIONS = {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
};

/**
 * Форматирует число в цену в рублях
 * @param {number} price - Число для форматирования
 * @returns {string} Отформатированная цена в рублях
 */
function formatPrice(price) {
  return `${price.toLocaleString('ru-RU', NUMBER_FORMAT_OPTIONS)} ₽`;
}

/**
 * Обновление всех курсов в интерфейсе
 */
async function updateAllPrices() {
  const refreshBtn = document.querySelector('.refresh-btn');
  const refreshIcon = refreshBtn.querySelector('i');
  
  // Добавляем анимацию вращения
  refreshIcon.style.animation = 'spin 1s linear infinite';
  
  try {
    const [btcPrice, ethPrice, tonPrice, fiatPrices] = await Promise.all([
      getBTCPriceFromBinance(),
      getETHPriceFromBinance(),
      getTONPriceFromBinance(),
      getFiatPricesFromMOEX()
    ]);

    // Обновляем цены с анимацией
    const priceElements = document.querySelectorAll('.asset-item .price');
    priceElements.forEach(element => {
      element.style.color = 'var(--accent-primary)';
      setTimeout(() => {
        element.style.color = 'var(--text-secondary)';
      }, 500);
    });

    // Обновляем значения
    document.querySelector('.asset-item:nth-child(1) .price').textContent = formatPrice(btcPrice);
    document.querySelector('.asset-item:nth-child(2) .price').textContent = formatPrice(ethPrice);
    document.querySelector('.asset-item:nth-child(3) .price').textContent = formatPrice(tonPrice);
    document.querySelector('.asset-item:nth-child(4) .price').textContent = formatPrice(fiatPrices.USD);
    document.querySelector('.asset-item:nth-child(5) .price').textContent = formatPrice(fiatPrices.EUR);
    document.querySelector('.asset-item:nth-child(6) .price').textContent = formatPrice(fiatPrices.CNY);
    document.querySelector('.asset-item:nth-child(7) .price').textContent = formatPrice(fiatPrices.AED);

    // Подстраиваем размер шрифта после обновления цен
    adjustPriceFontSize();
  } catch (error) {
    console.error('Ошибка при обновлении цен:', error);
  } finally {
    // Останавливаем анимацию вращения
    refreshIcon.style.animation = '';
  }
}

/**
 * Инициализация графиков и загрузка данных
 * 
 * Основная функция, которая:
 * 1. Загружает данные из JSON файла
 * 2. Создает графики криптовалют и фиатных валют
 * 3. Настраивает обработчики событий
 * 4. Обрабатывает ошибки загрузки
 */
async function initializeCharts() {
  try {
    // Загрузка данных из JSON файла
    const response = await fetch('exchangerates.json');
    const data = await response.json();
    let baseLabels = generateLabels("2023-01-01", 36);
    let cryptoChart, fiatChart;

    // Обновляем курс BTC каждые 30 секунд
    updateAllPrices();
    setInterval(updateAllPrices, 30000);

    /**
     * Обновление графиков при изменении интервала
     * @param {string} interval - Выбранный интервал
     */
    function updateCharts(interval) {
      const isDaily = interval === '1m';
      const labels = isDaily ? generateLabels(null, null, true) : baseLabels.slice(-getMonthCount(interval));

      // Подготовка данных для криптовалют
      const cryptoDatasets = Object.keys(data.crypto).map(currency => ({
        label: currency,
        data: getDataForInterval(data.crypto[currency], interval),
        tension: 0.3 // Сглаживание линий графика
      }));

      // Подготовка данных для фиатных валют
      const fiatDatasets = Object.keys(data.fiat).map(currency => ({
        label: currency,
        data: getDataForInterval(data.fiat[currency], interval),
        tension: 0.3
      }));

      // Создание или обновление графика криптовалют
      if (!cryptoChart) {
        const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
        cryptoChart = new Chart(cryptoCtx, createChartConfig('line', { labels: labels, datasets: cryptoDatasets }));
      } else {
        cryptoChart.data.labels = labels;
        cryptoChart.data.datasets = cryptoDatasets;
        cryptoChart.update();
      }

      // Создание или обновление графика фиатных валют
      if (!fiatChart) {
        const fiatCtx = document.getElementById('fiatChart').getContext('2d');
        fiatChart = new Chart(fiatCtx, createChartConfig('line', { labels: labels, datasets: fiatDatasets }));
      } else {
        fiatChart.data.labels = labels;
        fiatChart.data.datasets = fiatDatasets;
        fiatChart.update();
      }
    }

    /**
     * Определение количества месяцев для интервала
     * @param {string} interval - Выбранный интервал
     * @returns {number} Количество месяцев
     */
    function getMonthCount(interval) {
      switch(interval) {
        case '1m': return 1;
        case '6m': return 6;
        case '1y': return 12;
        case '3y': return 36;
        default: return 36;
      }
    }

    // Инициализация с дефолтным интервалом (3 года)
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

/**
 * Управление темами оформления
 * 
 * Функционал включает:
 * 1. Загрузку сохраненной темы
 * 2. Переключение тем через селектор
 * 3. Переключение тем через кнопку
 * 4. Сохранение выбранной темы
 * 5. Обновление иконки темы
 */
document.addEventListener('DOMContentLoaded', () => {
  const themeSelect = document.getElementById('colorScheme');
  const themeToggle = document.querySelector('.theme-toggle');
  const themeIcon = themeToggle.querySelector('i');

  // Загрузка сохраненной темы из localStorage
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  themeSelect.value = savedTheme;
  updateThemeIcon(savedTheme);

  // Обработчик изменения темы через селектор
  themeSelect.addEventListener('change', handleThemeChange);

  // Обработчик переключения темы через кнопку
  themeToggle.addEventListener('click', handleThemeToggle);

  // Добавляем обработчик для кнопки обновления
  const refreshBtn = document.querySelector('.refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', updateAllPrices);
  }

  /**
   * Обработчик изменения темы через селектор
   * @param {Event} e - Событие изменения
   */
  function handleThemeChange(e) {
    const theme = e.target.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
    location.reload(); // Перезагрузка страницы для применения новой темы
  }

  /**
   * Обработчик переключения темы через кнопку
   */
  function handleThemeToggle() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themes = ['light', 'dark', 'colorblind'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    
    document.documentElement.setAttribute('data-theme', nextTheme);
    themeSelect.value = nextTheme;
    localStorage.setItem('theme', nextTheme);
    updateThemeIcon(nextTheme);
    location.reload(); // Перезагрузка страницы для применения новой темы
  }

  /**
   * Обновление иконки темы
   * @param {string} theme - Текущая тема
   */
  function updateThemeIcon(theme) {
    switch(theme) {
      case 'dark':
        themeIcon.className = 'fas fa-moon';
        break;
      case 'light':
        themeIcon.className = 'fas fa-sun';
        break;
      case 'colorblind':
        themeIcon.className = 'fas fa-eye';
        break;
    }
  }
});

// Добавляем обработчик изменения размера окна
window.addEventListener('resize', adjustPriceFontSize);

// Добавляем обработчик для кнопки обновления
document.querySelector('.refresh-btn').addEventListener('click', updateAllPrices);

// Вызываем функцию при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  updateAllPrices();
  // Обновляем цены каждые 30 секунд
  setInterval(updateAllPrices, 30000);
}); 