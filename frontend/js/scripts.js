
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
      // Проверяем, доступна ли функция updateAllPrices
      if (typeof updateAllPrices === 'function') {
        updateAllPrices(); // Вызываем функцию обновления всех цен
      } else {
        console.warn('Функция updateAllPrices не найдена. Возможно, не загружен dashboardScripts.js');
      }
    });
  }
}

/**
 * Инициализация системы уведомлений
 */
function initNotifications() {
  console.log('Инициализация уведомлений');

  // Загружаем сохраненные настройки
  loadNotificationSettings();

  // Инициализация статуса уведомлений для текущей валюты
  const currentCurrency = document.getElementById('notifyCurrency');
  if (currentCurrency) {
    updateNotificationStatus(currentCurrency.value);
  }

  // Добавляем обработчик формы настроек
  const settingsForms = document.querySelectorAll('.settings-form');
  if (settingsForms.length > 0) {
    settingsForms.forEach(form => {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showNotificationMessage('Настройки успешно сохранены');
        } else {
          showNotificationMessage('Ошибка при сохранении настроек', 'error');
        }
      })
      .catch(error => {
        console.error('Ошибка:', error);
        showNotificationMessage('Произошла ошибка при сохранении', 'error');
      });
    });
    });
  }
}

// Объект для хранения состояния уведомлений по валютам
let currencyNotifications = {
  BTC: { enabled: true, times: [9, 12, 15, 18] },
  ETH: { enabled: true, times: [8, 12, 16, 20] },
  TON: { enabled: true, times: [10, 14, 18, 22] },
  USD: { enabled: true, times: [8, 12, 16, 20] },
  EUR: { enabled: true, times: [8, 12, 16, 20] },
  CNY: { enabled: true, times: [7, 11, 15, 19] },
  AED: { enabled: true, times: [8, 12, 16, 20] }
};

// Функция включения/выключения уведомлений для валюты
function toggleNotifications(currency, enabled) {
  if (currencyNotifications[currency]) {
    currencyNotifications[currency].enabled = enabled;
    if (enabled && currencyNotifications[currency].times.length === 0) {
      // Устанавливаем стандартное время для уведомлений при включении
      currencyNotifications[currency].times = [8, 12, 16, 20];
    }
    saveNotificationSettings();
    updateNotificationStatus(currency);
  }
}

// Загрузка сохраненных настроек из localStorage
function loadNotificationSettings() {
  const saved = localStorage.getItem('currencyNotifications');
  if (saved) {
    try {
      currencyNotifications = JSON.parse(saved);
    } catch (e) {
      console.warn('Ошибка загрузки настроек уведомлений:', e);
    }
  }
}

// Сохранение настроек в localStorage
function saveNotificationSettings() {
  localStorage.setItem('currencyNotifications', JSON.stringify(currencyNotifications));
}

// Функция обновления статуса уведомлений при переключении валюты
function updateNotificationStatus(currency) {
  const statusElement = document.getElementById('notificationStatus');
  const timelineElement = document.getElementById('notificationTimeline');
  const timeSelectionContainer = document.getElementById('timeSelectionContainer');

  if (!statusElement || !timelineElement) return;

  const currencyInfo = currencyNotifications[currency];

  // Обновляем статус
  if (currencyInfo.enabled) {
    statusElement.innerHTML = `<strong>Уведомления включены</strong> для ${currency}`;
    statusElement.classList.remove('notification-disabled');
    
    // Показываем временную шкалу
    timelineElement.style.display = 'block';
    timelineElement.innerHTML = generateTimeline(currencyInfo.times, currency);
    
    // Показываем контейнер выбора времени
    if (timeSelectionContainer) {
      timeSelectionContainer.style.display = 'block';
      generateTimeSelection(currency);
    }
  } else {
    statusElement.innerHTML = `Уведомления отключены для ${currency}`;
    statusElement.classList.add('notification-disabled');
    timelineElement.style.display = 'none';
    if (timeSelectionContainer) {
      timeSelectionContainer.style.display = 'none';
    }
  }
}

// Функция генерации временной шкалы
function generateTimeline(times, currency) {
  if (!times.length) return '<em>Время уведомлений не выбрано</em>';

  let timeline = '<strong>Время уведомлений:</strong><br>';
  times.forEach(time => {
    timeline += `<span class="timeline-marker" title="${time}:00"></span> ${time}:00 `;
  });
  timeline += '<br><small style="color: var(--text-secondary);">Нажмите на время ниже, чтобы изменить</small>';

  return timeline;
}

// Функция генерации интерфейса выбора времени
function generateTimeSelection(currency) {
  const container = document.querySelector('.time-checkboxes');
  if (!container) return;

  const currentTimes = currencyNotifications[currency].times;
  const availableHours = Array.from({length: 24}, (_, i) => i);

  container.innerHTML = '';
  availableHours.forEach(hour => {
    const isChecked = currentTimes.includes(hour);
    const checkboxItem = document.createElement('div');
    checkboxItem.className = 'time-checkbox-item';
    
    checkboxItem.innerHTML = `
      <input type="checkbox" id="time_${hour}" value="${hour}" ${isChecked ? 'checked' : ''}>
      <label for="time_${hour}">${hour.toString().padStart(2, '0')}:00</label>
    `;
    
    container.appendChild(checkboxItem);
  });
}

// Функция сохранения выбранного времени уведомлений
function saveNotificationTimes() {
  const currentCurrency = document.getElementById('notifyCurrency').value;
  const checkboxes = document.querySelectorAll('.time-checkboxes input[type="checkbox"]:checked');
  
  const selectedTimes = Array.from(checkboxes).map(cb => parseInt(cb.value)).sort((a, b) => a - b);
  
  // Обновляем настройки для текущей валюты
  currencyNotifications[currentCurrency].times = selectedTimes;
  
  // Сохраняем в localStorage
  saveNotificationSettings();
  
  // Обновляем отображение
  updateNotificationStatus(currentCurrency);
  
  // Показываем уведомление об успешном сохранении
  showNotificationMessage('Время уведомлений сохранено!');
}

// Функция показа временного уведомления
function showNotificationMessage(message) {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--accent-primary);
    color: white;
    padding: 10px 20px;
    border-radius: var(--border-radius);
    z-index: 1000;
    animation: slideIn 0.3s ease;
  `;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
}
