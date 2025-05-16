
  // Переключение темы
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });



document.addEventListener('DOMContentLoaded', function() {
    let remainingSeconds = initialSeconds;
    const timerElement = document.getElementById('timer');

    function updateTimer() {
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;

        timerElement.textContent =
            `Код действителен еще: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (remainingSeconds <= 0) {
            timerElement.textContent = 'Срок действия кода истек';
            return;
        }

        remainingSeconds--;
        setTimeout(updateTimer, 1000);
    }

    // Запускаем таймер
    updateTimer();

    // Код для повторной отправки...
    document.getElementById('resend-btn')?.addEventListener('click', function(e) {
        e.preventDefault();
        fetch('/resend-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `email=${encodeURIComponent('{{ email }}')}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                remainingSeconds = 300; // 5 минут
                updateTimer();
                alert('Новый код отправлен!');
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        });
    });
});