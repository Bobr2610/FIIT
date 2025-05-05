// Добавим новые константы в начало файла
const CURRENCY_INFO = {
  crypto: {
    BTC: {
      name: 'Bitcoin',
      description: 'Bitcoin - первая и самая популярная криптовалюта в мире. Создана в 2009 году.',
      color: '#F7931A'
    },
    ETH: {
      name: 'Ethereum',
      description: 'Ethereum - платформа для создания децентрализованных приложений на блокчейне.',
      color: '#627EEA'
    },
    TON: {
      name: 'Toncoin',
      description: 'TON - быстрая и масштабируемая блокчейн-платформа.',
      color: '#0088CC'
    }
  },
  fiat: {
    USD: {
      name: 'Доллар США',
      description: 'Доллар США - основная резервная валюта мира.',
      color: '#85bb65'
    },
    EUR: {
      name: 'Евро',
      description: 'Евро - единая валюта Европейского союза.',
      color: '#0066ff'
    },
    CNY: {
      name: 'Китайский Юань',
      description: 'Юань - официальная валюта Китайской Народной Республики.',
      color: '#ff0000'
    },
    AED: {
      name: 'Дирхам ОАЭ',
      description: 'Дирхам - официальная валюта Объединенных Арабских Эмиратов.',
      color: '#00732f'
    }
  }
};

// Добавим переменные для текущих валют
let currentCrypto = 'BTC';
let currentFiat = 'USD';

// Глобальная переменная для хранения загруженных данных
let chartData = null;

// Запуск инициализации при загрузке страницы
window.addEventListener('load', initializeCharts);

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
  if (!data) {
    console.warn('Нет данных для выбранной валюты!');
    return [];
  }
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
          type: 'logarithmic',
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
        // AEDRUB_TOD - дирхам ОАЭ
        else if (secId === 'AEDRUB_TOD') {
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
  if (price === undefined || price === null || isNaN(price)) {
    return '— ₽';
  }
  
  // Округляем до соответствующей точности в зависимости от величины числа
  let formattedPrice;
  if (price >= 1000000) {
    // Для больших чисел (миллионы+) округляем до тысяч
    formattedPrice = (Math.round(price / 1000) / 1000).toLocaleString('ru-RU', {
      minimumFractionDigits: 3,
      maximumFractionDigits: 3
    }) + ' млн ₽';
  } else if (price >= 10000) {
    // Для чисел от 10,000 до 999,999 округляем до целых
    formattedPrice = Math.round(price).toLocaleString('ru-RU') + ' ₽';
  } else if (price >= 100) {
    // Для средних чисел (100-9,999) округляем до десятых
    formattedPrice = price.toLocaleString('ru-RU', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }) + ' ₽';
  } else {
    // Для маленьких чисел используем два десятичных разряда
    formattedPrice = price.toLocaleString('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }) + ' ₽';
  }
  
  return formattedPrice;
}

/**
 * Обновление всех курсов в интерфейсе
 * 
 * Функция:
 * 1. Получает актуальные цены с бирж
 * 2. Обновляет отображение цен с анимацией
 * 3. Подстраивает размер шрифта
 * 4. Обрабатывает возможные ошибки
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

    // Обновляем значения с проверкой на undefined
    const prices = [
      btcPrice,
      ethPrice,
      tonPrice,
      fiatPrices?.USD,
      fiatPrices?.EUR,
      fiatPrices?.CNY,
      fiatPrices?.AED
    ];

    priceElements.forEach((element, index) => {
      element.textContent = formatPrice(prices[index]);
    });

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
 * Обновление информации о валюте
 * @param {string} type - Тип валюты ('crypto' или 'fiat')
 * @param {string} currency - Код валюты
 * @param {Array} data - Массив данных для расчета статистики
 */
function updateCurrencyInfo(type, currency, data) {
  const container = document.querySelector(`#${type}Assets`);
  const info = CURRENCY_INFO[type][currency];
  
  // Обновляем название и описание
  container.querySelector('.currency-name').textContent = `${info.name} (${currency})`;
  container.querySelector('.currency-details').textContent = info.description;
  container.querySelector('.current-currency').textContent = currency;
  
  // Рассчитываем статистику
  const stats = calculateStats(data);
  
  // Обновляем статистику с анимацией
  const elements = {
    median: container.querySelector('.median'),
    average: container.querySelector('.average'),
    outliers: container.querySelector('.outliers')
  };
  
  // Добавляем класс для анимации
  Object.values(elements).forEach(el => el.classList.add('updating'));
  
  // Обновляем значения с задержкой для анимации
  setTimeout(() => {
    elements.median.textContent = formatPrice(stats.median);
    elements.average.textContent = formatPrice(stats.average);
    elements.outliers.textContent = stats.outliers;
    
    // Убираем класс анимации
    Object.values(elements).forEach(el => el.classList.remove('updating'));
  }, 300);
}

/**
 * Расчет статистических показателей
 * @param {Array} data - Массив значений
 * @returns {Object} Объект со статистическими показателями
 */
function calculateStats(data) {
  if (!data || data.length === 0) {
    return {
      median: 0,
      average: 0,
      outliers: '0 значений'
    };
  }

  // Копируем данные и сортируем для расчетов
  const sortedData = [...data].sort((a, b) => a - b);
  const n = sortedData.length;
  
  // Медиана
  let median;
  if (n % 2 === 0) {
    // Для четного количества элементов берем среднее двух центральных
    median = (sortedData[n/2 - 1] + sortedData[n/2]) / 2;
  } else {
    // Для нечетного берем центральный
    median = sortedData[Math.floor(n/2)];
  }
  
  // Среднее значение - сумма всех значений, деленная на их количество
  const sum = sortedData.reduce((acc, value) => acc + value, 0);
  const average = sum / n;
  
  // Расчет выбросов по методу межквартильного размаха (IQR)
  const q1Index = Math.floor(n * 0.25);
  const q3Index = Math.floor(n * 0.75);
  
  const q1 = sortedData[q1Index]; // 1й квартиль (25%)
  const q3 = sortedData[q3Index]; // 3й квартиль (75%)
  
  const iqr = q3 - q1; // Межквартильный размах
  
  // Границы для определения выбросов
  const lowerBound = q1 - 1.5 * iqr;
  const upperBound = q3 + 1.5 * iqr;
  
  // Подсчет выбросов - значений, выходящих за границы
  const outliers = sortedData.filter(value => 
    value < lowerBound || value > upperBound
  ).length;
  
  return {
    median,
    average,
    outliers: `${outliers} знач.`
  };
}

/**
 * Обработчики для кнопок покупки и продажи
 */
function initTradingButtons() {
  document.querySelectorAll('.trading-buttons').forEach(container => {
    const buyBtn = container.querySelector('.buy-btn');
    const sellBtn = container.querySelector('.sell-btn');
    
    buyBtn.addEventListener('click', () => {
      alert('Функция покупки будет доступна в следующем обновлении');
    });
    
    sellBtn.addEventListener('click', () => {
      alert('Функция продажи будет доступна в следующем обновлении');
    });
  });
}

/**
 * Инициализация переключателей валют
 */
function initCurrencySelectors() {
  ['crypto', 'fiat'].forEach(type => {
    const container = document.querySelector(`#${type}Assets`);
    const currencies = Object.keys(CURRENCY_INFO[type]);
    const prevBtn = container.querySelector('.selector-btn.prev');
    const nextBtn = container.querySelector('.selector-btn.next');
    
    function updateCurrency(direction) {
      const currentValue = type === 'crypto' ? currentCrypto : currentFiat;
      const currentIndex = currencies.indexOf(currentValue);
      const newIndex = (currentIndex + direction + currencies.length) % currencies.length;
      const newCurrency = currencies[newIndex];
      
      if (type === 'crypto') {
        currentCrypto = newCurrency;
      } else {
        currentFiat = newCurrency;
      }
      
      // Получаем текущий интервал
      const timeRange = document.getElementById('timeRange');
      updateCharts(timeRange.value);
    }
    
    prevBtn.addEventListener('click', () => updateCurrency(-1));
    nextBtn.addEventListener('click', () => updateCurrency(1));
  });
}

/**
 * Определение количества месяцев для интервала
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

// Маппинг для ключей фиатных валют
const fiatKeyMap = {
    USD: 'USD/RUB',
    EUR: 'EUR/RUB',
    CNY: 'CNY/RUB',
    AED: 'AED/RUB'
};

// Модифицируем функцию updateCharts
function updateCharts(interval) {
  if (!chartData) {
    console.error('Данные графиков не загружены');
    return;
  }

  const isDaily = interval === '1m';
  const labels = isDaily ? generateLabels(null, null, true) : baseLabels.slice(-getMonthCount(interval));

  // Подготовка данных для криптовалют
  const cryptoData = getDataForInterval(chartData.crypto[currentCrypto], interval);
  const cryptoDatasets = [{
    label: currentCrypto,
    data: cryptoData,
    borderColor: CURRENCY_INFO.crypto[currentCrypto].color,
    tension: 0.3
  }];

  // Подготовка данных для фиатных валют (с учетом правильного ключа)
  const fiatData = getDataForInterval(chartData.fiat[fiatKeyMap[currentFiat]], interval);
  const fiatDatasets = [{
    label: currentFiat,
    data: fiatData,
    borderColor: CURRENCY_INFO.fiat[currentFiat].color,
    tension: 0.3
  }];

  // Настройки для графиков
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: { enabled: true }
    },
    scales: {
      x: {
        display: true,
        grid: { display: false },
        ticks: {
          maxRotation: 0,
          autoSkip: true,
          maxTicksLimit: 12
        }
      },
      y: {
        type: 'logarithmic',
        display: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    }
  };

  // Обновление графиков
  if (!window.cryptoChart) {
    const cryptoCtx = document.getElementById('cryptoChart').getContext('2d');
    window.cryptoChart = new Chart(cryptoCtx, {
      type: 'line',
      data: { labels, datasets: cryptoDatasets },
      options: chartOptions
    });
  } else {
    window.cryptoChart.data.labels = labels;
    window.cryptoChart.data.datasets = cryptoDatasets;
    window.cryptoChart.update('none');
  }

  if (!window.fiatChart) {
    const fiatCtx = document.getElementById('fiatChart').getContext('2d');
    window.fiatChart = new Chart(fiatCtx, {
      type: 'line',
      data: { labels, datasets: fiatDatasets },
      options: chartOptions
    });
  } else {
    window.fiatChart.data.labels = labels;
    window.fiatChart.data.datasets = fiatDatasets;
    window.fiatChart.update('none');
  }

  // Обновляем информацию о валютах
  updateCurrencyInfo('crypto', currentCrypto, cryptoData);
  updateCurrencyInfo('fiat', currentFiat, fiatData);
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
    const response = await fetch(exchangeratesFile);
    chartData = await response.json();
    
    // Генерируем метки для временной оси
    window.baseLabels = generateLabels("2023-01-01", 36);

    // Инициализация переключателей валют
    initCurrencySelectors();
    
    // Инициализация кнопок торговли
    initTradingButtons();

    // Обновляем графики с начальными значениями
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

/**
 * Получение финансовых новостей из API РБК через CORS-прокси
 * 
 * Функция выполняет следующие действия:
 * 1. Делает запрос к API РБК через CORS-прокси
 * 2. Парсит полученный HTML
 * 3. Извлекает первые 8 новостей
 * 4. В случае ошибки показывает заглушку
 * 
 * @returns {Promise<Array>} Массив новостей в формате:
 *   {
 *     text: string,      // Текст новости
 *     link: string,      // Ссылка на новость
 *     category: string,  // Категория новости
 *     description: string // Описание новости (пустое)
 *   }
 */
async function getFinancialNews() {
  try {
    const corsProxy = 'https://api.allorigins.win/raw?url=';
    const targetUrl = encodeURIComponent('https://www.rbc.ru/api/v1/finance/news');
    
    const response = await fetch(corsProxy + targetUrl, {
      method: 'GET',
      headers: {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Origin': window.location.origin,
        'Referer': 'https://www.rbc.ru/'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const htmlText = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');
    
    // Находим корневой элемент с новостями
    const newsHeader = doc.querySelector('.error__news__header');
    if (!newsHeader) {
      throw new Error('Заголовок новостей не найден');
    }
    
    // Находим все новостные блоки и берем только первые 8
    const newsItems = Array.from(newsHeader.parentElement.querySelectorAll('.error__news__item')).slice(0, 8);
    
    // Обрабатываем новости
    const news = newsItems.map(item => {
      const linkElement = item.querySelector('.error__news__link');
      const titleElement = item.querySelector('.error__news__title');
      
      return {
        text: titleElement ? titleElement.textContent.trim() : '',
        link: linkElement ? linkElement.href : '#',
        category: 'Новости', // По умолчанию, так как категория не указана в HTML
        description: '' // Описание отсутствует в текущей структуре
      };
    }).filter(item => item.text); // Фильтруем пустые новости
    
    if (news.length > 0) {
      updateNewsList(news);
      return news;
    }
    
    throw new Error('Новости не найдены в HTML');
    
  } catch (error) {
    console.error('Ошибка при получении новостей:', error);
    
    // В случае ошибки показываем заглушку (тоже ограничиваем до 8 новостей)
    const fallbackNews = [
      { text: 'Рынок криптовалют демонстрирует повышенную волатильность', link: '#', category: 'Финансы', description: '' },
      { text: 'Евро укрепился на фоне свежих экономических данных', link: '#', category: 'Экономика', description: '' },
      { text: 'Рубль стабилизируется по отношению к USD', link: '#', category: 'Финансы', description: '' },
      { text: 'L\'Oreal предостерег ЕС от «красного флага» на косметику', link: '#', category: 'Бизнес', description: '' },
      { text: 'Курс доллара в апреле 2025 года: чем закончится трехмесячное ралли рубля', link: '#', category: 'Финансы', description: '' }
    ].slice(0, 8);
    updateNewsList(fallbackNews);
    return fallbackNews;
  }
}

/**
 * Обновление списка новостей на странице
 * 
 * Функция:
 * 1. Находит элемент списка новостей
 * 2. Преобразует массив новостей в HTML-разметку
 * 3. Обновляет содержимое списка
 * 
 * @param {Array} news - Массив новостей для отображения
 */
function updateNewsList(news) {
  const newsList = document.querySelector('.news-list');
  if (!newsList) return;
  
  newsList.innerHTML = news.map(item => `
    <li>
      <a href="${item.link}" target="_blank" rel="noopener noreferrer">
        ${item.text}
      </a>
      ${item.description ? `<p class="news-description">${item.description}</p>` : ''}
    </li>
  `).join('');
}

// Добавляем вызов функции при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  // ... existing code ...
  
  // Получаем новости каждые 5 минут
  getFinancialNews();
  setInterval(getFinancialNews, 5 * 60 * 1000);
});

// --- Переключение валют для графиков (crypto/fiat) ---
function setupCurrencySwitchers() {
  // Криптовалюты
  const cryptoPrev = document.querySelector('#cryptoAssets .selector-btn.prev');
  const cryptoNext = document.querySelector('#cryptoAssets .selector-btn.next');
  cryptoPrev.addEventListener('click', () => {
    const keys = Object.keys(CURRENCY_INFO.crypto);
    let idx = keys.indexOf(currentCrypto);
    idx = (idx - 1 + keys.length) % keys.length;
    currentCrypto = keys[idx];
    const timeRange = document.getElementById('timeRange');
    updateCharts(timeRange.value);
  });
  cryptoNext.addEventListener('click', () => {
    const keys = Object.keys(CURRENCY_INFO.crypto);
    let idx = keys.indexOf(currentCrypto);
    idx = (idx + 1) % keys.length;
    currentCrypto = keys[idx];
    const timeRange = document.getElementById('timeRange');
    updateCharts(timeRange.value);
  });
  // Фиатные валюты
  const fiatPrev = document.querySelector('#fiatAssets .selector-btn.prev');
  const fiatNext = document.querySelector('#fiatAssets .selector-btn.next');
  fiatPrev.addEventListener('click', () => {
    const keys = Object.keys(CURRENCY_INFO.fiat);
    let idx = keys.indexOf(currentFiat);
    idx = (idx - 1 + keys.length) % keys.length;
    currentFiat = keys[idx];
    const timeRange = document.getElementById('timeRange');
    updateCharts(timeRange.value);
  });
  fiatNext.addEventListener('click', () => {
    const keys = Object.keys(CURRENCY_INFO.fiat);
    let idx = keys.indexOf(currentFiat);
    idx = (idx + 1) % keys.length;
    currentFiat = keys[idx];
    const timeRange = document.getElementById('timeRange');
    updateCharts(timeRange.value);
  });
}

// --- Автоматическое обновление графиков при смене темы ---
function setupThemeChartRefresh() {
  const themeSelect = document.getElementById('colorScheme');
  if (themeSelect) {
    themeSelect.addEventListener('change', () => {
      setTimeout(() => {
        const timeRange = document.getElementById('timeRange');
        updateCharts(timeRange.value);
      }, 300); // Ждём применения темы
    });
  }
  // Также слушаем событие изменения data-theme (например, при переключении кнопкой)
  const observer = new MutationObserver(() => {
    const timeRange = document.getElementById('timeRange');
    updateCharts(timeRange.value);
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
}

// --- Инициализация ---
document.addEventListener('DOMContentLoaded', () => {
  setupCurrencySwitchers();
  setupThemeChartRefresh();
}); 
