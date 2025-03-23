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
    return data.daily_2025_01 || [];
  }
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
  // Получаем CSS переменные для цветов
  const getComputedStyle = window.getComputedStyle(document.documentElement);
  const getColor = (currency) => {
    // Преобразуем название валюты в формат для CSS переменной
    const currencyKey = currency.split('/')[0].toLowerCase();
    const color = getComputedStyle.getPropertyValue(`--chart-${currencyKey}-color`).trim();
    const bgColor = color.replace(')', `, ${getComputedStyle.getPropertyValue('--chart-bg-opacity').trim()})`);
    return {
      borderColor: color,
      backgroundColor: bgColor
    };
  };

  return {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        ...getColor(dataset.label)
      }))
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
        cryptoChart = new Chart(cryptoCtx, createChartConfig('line', {
          labels: labels,
          datasets: cryptoDatasets
        }, {
          y: {
            type: 'logarithmic', // Логарифмическая шкала для лучшего отображения
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

      // Создание или обновление графика фиатных валют
      if (!fiatChart) {
        const fiatCtx = document.getElementById('fiatChart').getContext('2d');
        fiatChart = new Chart(fiatCtx, createChartConfig('line', {
          labels: labels,
          datasets: fiatDatasets
        }, {
          y: {
            type: 'logarithmic',
            ticks: {
              callback: function(value) {
                return value;
              }
            }
          },
          yAxisTitle: 'Курс (RUB)'
        }));
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
  themeSelect.addEventListener('change', (e) => {
    const theme = e.target.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
  });

  // Обработчик переключения темы через кнопку
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themes = ['light', 'dark', 'colorblind'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    
    document.documentElement.setAttribute('data-theme', nextTheme);
    themeSelect.value = nextTheme;
    localStorage.setItem('theme', nextTheme);
    updateThemeIcon(nextTheme);
  });

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