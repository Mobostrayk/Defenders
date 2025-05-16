// Переключение темы
const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

document.documentElement.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Элементы модального окна
const settingsModal = document.getElementById('settings-modal');
const openSettingsBtn = document.getElementById('open-settings');
const closeSettingsBtn = document.getElementById('close-settings');
const cancelSettingsBtn = document.getElementById('cancel-settings');
const avatarForm = document.getElementById('avatar-form');
const passwordForm = document.getElementById('password-form');
const fileInput = document.getElementById('avatar-upload');
const fileName = document.getElementById('file-name');

// Управление модальным окном
if (openSettingsBtn && settingsModal) {
    openSettingsBtn.addEventListener('click', () => {
        settingsModal.style.display = 'flex';
    });
}

if (closeSettingsBtn) {
    closeSettingsBtn.addEventListener('click', closeModal);
}

if (cancelSettingsBtn) {
    cancelSettingsBtn.addEventListener('click', closeModal);
}

window.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        closeModal();
    }
});

// Обработка выбора файла
if (fileInput && fileName) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;

            // Автоматическая отправка формы при выборе файла
            const formData = new FormData(avatarForm);
            formData.append('avatar', fileInput.files[0]);

            fetch(avatarForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Обновляем аватар на странице
                    const avatarImg = document.querySelector('.avatar-image');
                    if (avatarImg) {
                        avatarImg.src = data.avatar_url + '?t=' + new Date().getTime();
                    } else {
                        // Если аватар был дефолтный, создаем img
                        const placeholder = document.querySelector('.avatar-placeholder');
                        if (placeholder) {
                            placeholder.innerHTML = `<img src="${data.avatar_url}" alt="Аватар" class="avatar-image">`;
                        }
                    }
                    showMessage('Аватар успешно обновлен', 'success');
                } else {
                    showMessage(data.message || 'Ошибка обновления аватара', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Ошибка загрузки аватара', 'error');
            });
        }
    });
}

// Валидация и отправка формы пароля
if (passwordForm) {
    passwordForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const oldPassword = this.querySelector('[name="old_password"]').value;
        const newPassword1 = this.querySelector('[name="new_password1"]').value;
        const newPassword2 = this.querySelector('[name="new_password2"]').value;

        // Валидация пароля
        if (newPassword1.length < 8) {
            showMessage('Пароль должен содержать минимум 8 символов', 'error');
            return;
        }

        if (newPassword1 !== newPassword2) {
            showMessage('Новые пароли не совпадают', 'error');
            return;
        }

        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showMessage('Пароль успешно изменен', 'success');
                this.reset();
            } else {
                showMessage(data.message || 'Ошибка изменения пароля', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Ошибка изменения пароля', 'error');
        });
    });
}

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
                    showMessage('Привычка удалена', 'success');
                } else {
                    showMessage(data.message || 'Ошибка при удалении привычки', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Произошла ошибка при удалении привычки', 'error');
            });
        }
    });
});

// Вспомогательные функции
function closeModal() {
    settingsModal.style.display = 'none';
}

function showMessage(text, type) {
    // Удаляем предыдущие сообщения
    const oldMessages = document.querySelectorAll('.alert-message');
    oldMessages.forEach(msg => msg.remove());

    const message = document.createElement('div');
    message.className = `alert-message ${type}`;
    message.textContent = text;

    document.body.appendChild(message);

    setTimeout(() => {
        message.classList.add('fade-out');
        setTimeout(() => message.remove(), 500);
    }, 3000);
}

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