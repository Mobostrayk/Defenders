// Переключение темы
const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

document.documentElement.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Управление модальным окном настроек
const settingsModal = document.getElementById('settings-modal');
const openSettingsBtn = document.getElementById('open-settings');
const closeSettingsBtn = document.getElementById('close-settings');

openSettingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'block';
});

closeSettingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.style.display = 'none';
    }
});

// Удаление привычек
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const habitId = this.getAttribute('data-habit-id');
        if (confirm('Вы уверены, что хотите удалить эту привычку?')) {
            fetch(`/habits/delete/${habitId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.closest('.habit-card').remove();
                } else {
                    alert(data.message || 'Ошибка при удалении привычки');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении привычки');
            });
        }
    });
});

// Функция для получения CSRF токена
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