
/**
 * Основной файл скриптов для FIIT
 * Управляет темами, временем и уведомлениями
 */
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM загружен, инициализация всех компонентов');

  // Инициализация темы
  initThemeManagement();

  // Инициализация уведомлений
  initNotifications();

  // Обновление времени
  initDateTime();

  // Инициализация кнопки обновления
  initRefreshButton();
});

/**
 * Инициализация управления темами
 */
function initThemeManagement() {
  const themeSelect = document.getElementById('colorScheme');
  const themeToggle = document.querySelector('.theme-toggle');
  const logoImage = document.getElementById('logoImage'); // Добавляем ссылку на логотип

  // Проверка наличия элементов темы
  if (!themeSelect || !themeToggle) {
    console.log('Элементы управления темой не найдены');
    return;
  }

  const themeIcon = themeToggle.querySelector('i');

  // Загрузка сохраненной темы из localStorage
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  themeSelect.value = savedTheme;
  updateThemeIcon(savedTheme, themeIcon);
  updateLogo(savedTheme, logoImage); // Обновляем логотип при инициализации

  // Обработчик изменения темы через селектор
  themeSelect.addEventListener('change', function(e) {
    const theme = e.target.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme, themeIcon);
    updateLogo(theme, logoImage); // Обновляем логотип при смене темы
    location.reload(); // Перезагрузка страницы для применения новой темы
  });

  // Обработчик переключения темы через кнопку
  themeToggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themes = ['light', 'dark', 'colorblind'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];

    document.documentElement.setAttribute('data-theme', nextTheme);
    themeSelect.value = nextTheme;
    localStorage.setItem('theme', nextTheme);
    updateThemeIcon(nextTheme, themeIcon);
    updateLogo(nextTheme, logoImage); // Обновляем логотип при смене темы
    location.reload(); // Перезагрузка страницы для применения новой темы
  });
}

/**
 * Обновление иконки темы
 * @param {string} theme - Текущая тема
 * @param {Element} iconElement - Элемент иконки
 */
function updateThemeIcon(theme, iconElement) {
  if (!iconElement) return;

  switch(theme) {
    case 'dark':
      iconElement.className = 'fas fa-moon';
      break;
    case 'light':
      iconElement.className = 'fas fa-sun';
      break;
    case 'colorblind':
      iconElement.className = 'fas fa-eye';
      break;
  }
}

/**
 * Обновление логотипа в зависимости от темы
 * @param {string} theme - Текущая тема
 * @param {Element} logoElement - Элемент изображения логотипа
 */
function updateLogo(theme, logoElement) {
  if (!logoElement) {
    console.log('Элемент логотипа не найден');
    return;
  }
  // Пути к изображениям логотипов необходимо будет скорректировать
  // в зависимости от того, как они доступны в вашем проекте (например, через Django staticfiles)
  // Здесь предполагается, что у вас есть переменные blackLogoPath и whiteLogoPath,
  // указывающие на правильные пути к файлам.
  const blackLogoPath = '/static/blacklogo.png'; // Обновленный путь без img/
  const whiteLogoPath = '/static/whitelogo.png'; // Обновленный путь без img/

  switch(theme) {
    case 'dark':
      logoElement.src = blackLogoPath;
      break;
    case 'light':
      logoElement.src = whiteLogoPath;
      break;
    case 'colorblind': // В режиме высокого контраста используется светлый логотип
      logoElement.src = whiteLogoPath;
      break;
    default:
      logoElement.src = whiteLogoPath; // Логотип по умолчанию
  }
}

/**
 * Инициализация даты и времени
 */
function initDateTime() {
  const timeElement = document.querySelector('.current-time');
  if (!timeElement) {
    console.log('Элемент времени не найден');
    return;
  }

  // Функция обновления времени
  function updateDateTime() {
    const now = new Date();
    const options = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    };

    timeElement.textContent = now.toLocaleString('ru-RU', options);
  }

  // Первоначальное обновление и установка интервала
  updateDateTime();
  setInterval(updateDateTime, 60000);
}

/**
 * Инициализация кнопки обновления
 */
function initRefreshButton() {
  const refreshBtn = document.querySelector('.refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      console.log('Обновление данных...');
      // Здесь должна быть функция updateAllPrices, но она не определена в вашем коде
      // Рекомендую определить её или вызывать другую функцию
    });
  }
}

/**
 * Инициализация системы уведомлений
 */
function initNotifications() {
  console.log('Инициализация уведомлений');

  const notificationToggle = document.getElementById('notificationToggle');
  const notificationPanel = document.getElementById('notificationPanel');

  console.log('Элементы уведомлений:', {
    notificationToggle: notificationToggle ? 'Найден' : 'Не найден',
    notificationPanel: notificationPanel ? 'Найден' : 'Не найден'
  });

  if (notificationToggle && notificationPanel) {
    console.log('Добавляем обработчик клика для уведомлений');

    // Прямая проверка работы обработчика
    notificationToggle.onclick = function(event) {
      console.log('Клик на кнопке уведомлений через onclick');
    };

    notificationToggle.addEventListener('click', function(event) {
      console.log('Кнопка уведомлений нажата через addEventListener');
      event.preventDefault();
      event.stopPropagation();

      // Проверяем текущее состояние
      const isHidden = notificationPanel.classList.contains('hidden');
      console.log('Текущее состояние панели: ' + (isHidden ? 'скрыта' : 'видима'));

      // Переключаем состояние
      notificationPanel.classList.toggle('hidden');

      // Проверяем новое состояние
      console.log('Новое состояние панели: ' +
        (notificationPanel.classList.contains('hidden') ? 'скрыта' : 'видима'));
    });

    // Закрывать панель при клике вне её
    document.addEventListener('click', function(event) {
      if (!notificationToggle.contains(event.target) &&
          !notificationPanel.contains(event.target)) {
        notificationPanel.classList.add('hidden');
      }
    });
  } else {
    console.log('Элементы уведомлений не найдены');
  }
}
