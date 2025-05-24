// Проверяем сохранённую тему при загрузке
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем предпочтения системы
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');

    document.documentElement.setAttribute('data-theme', savedTheme);

    // Добавляем кнопку переключения темы
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.setAttribute('aria-label', 'Toggle theme');
    themeToggle.innerHTML = savedTheme === 'dark' ? '☀️' : '🌙';
    themeToggle.addEventListener('click', toggleTheme);
    document.body.appendChild(themeToggle);
});

// Функция переключения темы
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Обновляем иконку кнопки
    const themeToggle = document.querySelector('.theme-toggle');
    themeToggle.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
}

// Слушаем изменения системных предпочтений
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem('theme')) {
        const newTheme = e.matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
    }
});
