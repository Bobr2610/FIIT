# Объяснение кода

## Функции для работы с новостями

### getFinancialNews()
```javascript
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
        category: 'Новости',
        description: ''
      };
    }).filter(item => item.text);
    
    if (news.length > 0) {
      updateNewsList(news);
      return news;
    }
    
    throw new Error('Новости не найдены в HTML');
    
  } catch (error) {
    console.error('Ошибка при получении новостей:', error);
    
    // В случае ошибки показываем заглушку
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
```

Функция `getFinancialNews()` отвечает за получение финансовых новостей с сайта РБК. Вот как она работает:

1. **Настройка запроса**:
   - Использует CORS-прокси (api.allorigins.win) для обхода ограничений браузера
   - Кодирует URL для безопасной передачи
   - Устанавливает необходимые заголовки для имитации браузера

2. **Получение данных**:
   - Делает GET-запрос к API РБК через прокси
   - Проверяет успешность ответа
   - Получает HTML-текст ответа

3. **Парсинг HTML**:
   - Создает DOM-парсер
   - Находит корневой элемент с новостями (`.error__news__header`)
   - Извлекает первые 8 новостных блоков

4. **Обработка новостей**:
   - Преобразует каждый блок в объект с текстом, ссылкой и категорией
   - Фильтрует пустые новости
   - Обновляет список новостей на странице

5. **Обработка ошибок**:
   - В случае ошибки показывает заглушку с предустановленными новостями
   - Логирует ошибки в консоль

### updateNewsList()
```javascript
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
```

Функция `updateNewsList()` обновляет список новостей на странице:

1. **Поиск элемента**:
   - Находит элемент с классом `.news-list`
   - Если элемент не найден, завершает работу

2. **Обновление содержимого**:
   - Преобразует массив новостей в HTML-разметку
   - Каждая новость представлена как ссылка
   - Добавляет описание, если оно есть
   - Устанавливает атрибуты безопасности для ссылок

## Функции для работы с ценами

### formatPrice()
```javascript
function formatPrice(price) {
  if (price === undefined || price === null) {
    return '— ₽';
  }
  return `${price.toLocaleString('ru-RU', NUMBER_FORMAT_OPTIONS)} ₽`;
}
```

Функция `formatPrice()` форматирует числовое значение в цену в рублях:

1. **Проверка значения**:
   - Проверяет, является ли цена undefined или null
   - В случае отсутствия значения возвращает "— ₽"

2. **Форматирование**:
   - Использует `toLocaleString()` для форматирования числа
   - Применяет настройки из `NUMBER_FORMAT_OPTIONS`
   - Добавляет символ рубля

### updateAllPrices()
```javascript
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
```

Функция `updateAllPrices()` обновляет все цены на странице:

1. **Подготовка**:
   - Находит кнопку обновления и её иконку
   - Запускает анимацию вращения

2. **Получение данных**:
   - Параллельно получает цены криптовалют и фиатных валют
   - Использует `Promise.all` для оптимизации запросов

3. **Обновление интерфейса**:
   - Находит все элементы с ценами
   - Добавляет анимацию изменения цвета
   - Обновляет значения с проверкой на undefined
   - Подстраивает размер шрифта

4. **Обработка ошибок**:
   - Логирует ошибки в консоль
   - Останавливает анимацию в любом случае

## Константы

### NUMBER_FORMAT_OPTIONS
```javascript
const NUMBER_FORMAT_OPTIONS = {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
};
```

Объект с настройками форматирования чисел:
- `minimumFractionDigits`: минимальное количество знаков после запятой
- `maximumFractionDigits`: максимальное количество знаков после запятой 