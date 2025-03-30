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

/**
 * Обновление даты и времени
 * 
 * Функция:
 * 1. Форматирует текущую дату и время
 * 2. Обновляет элемент на странице
 * 3. Обновляется каждую секунду
 */
function updateDateTime() {
  const timeElement = document.querySelector('.current-time');
  if (!timeElement) return;

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

// Добавляем вызов функции при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  // ... existing code ...
  
  // Обновляем время каждую минуту
  updateDateTime();
  setInterval(updateDateTime, 60000);
}); 