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

// Формы
const avatarForm = document.getElementById('avatar-form');
const passwordForm = document.getElementById('password-form');

// Элементы формы аватара
const fileInput = document.getElementById('avatar-upload');
const fileName = document.getElementById('file-name');
const avatarPreview = document.getElementById('avatar-preview');

// Открытие/закрытие модального окна
if (openSettingsBtn) {
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
window.addEventListener('click', e => {
    if (e.target === settingsModal) closeModal();
});

// Предпросмотр аватара
if (fileInput && fileName && avatarPreview) {
    fileInput.addEventListener('change', e => {
        const file = e.target.files[0];
        if (!file) return;

        fileName.textContent = file.name;

        const reader = new FileReader();
        reader.onload = ev => {
            if (avatarPreview.tagName === 'IMG') {
                avatarPreview.src = ev.target.result;
            } else {
                avatarPreview.innerHTML = `<img src="${ev.target.result}" alt="Аватар" class="avatar-image">`;
            }
        };
        reader.readAsDataURL(file);

        // Автоматическая отправка
        const formData = new FormData(avatarForm);
        fetch(avatarForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(res => res.json())
          .then(data => {
              if (data.status === 'success') showMessage('Аватар обновлён', 'success');
              else showMessage(data.message || 'Ошибка обновления аватара', 'error');
          })
          .catch(() => showMessage('Ошибка загрузки аватара', 'error'));
    });
}

// Валидация пароля
function validatePassword(password) {
    let errors = [];
    if (password.length < 8) {
        errors.push('Пароль должен содержать минимум 8 символов');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Добавьте хотя бы одну заглавную букву');
    }
    if (!/\d/.test(password)) {
        errors.push('Добавьте хотя бы одну цифру');
    }
    if (/^(.)\1+$/.test(password)) {
        errors.push('Слишком простой пароль');
    }
    return errors;
}

// Отправка формы пароля
if (passwordForm) {
    passwordForm.addEventListener('submit', e => {
        e.preventDefault();

        const oldPass = passwordForm.querySelector('[name="old_password"]').value.trim();
        const newPass1 = passwordForm.querySelector('[name="new_password1"]').value.trim();
        const newPass2 = passwordForm.querySelector('[name="new_password2"]').value.trim();

        clearError(passwordForm.querySelector('[name="old_password"]'), document.getElementById('old-password-error'));
        clearError(passwordForm.querySelector('[name="new_password1"]'), document.getElementById('new-password-error'));
        clearError(passwordForm.querySelector('[name="new_password2"]'), document.getElementById('password2-error'));

        let isValid = true;

        if (!oldPass) {
            showError(passwordForm.querySelector('[name="old_password"]'), document.getElementById('old-password-error'), 'Введите текущий пароль');
            isValid = false;
        }

        const passErrors = validatePassword(newPass1);
        if (passErrors.length > 0) {
            showError(passwordForm.querySelector('[name="new_password1"]'), document.getElementById('new-password-error'), passErrors.join('<br>'));
            isValid = false;
        }

        if (newPass1 !== newPass2) {
            showError(passwordForm.querySelector('[name="new_password2"]'), document.getElementById('password2-error'), 'Пароли не совпадают');
            isValid = false;
        }

        if (!isValid) return;

        const formData = new FormData(passwordForm);
        fetch(passwordForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(res => res.json())
          .then(data => {
              if (data.status === 'success') {
                  showMessage('Пароль изменен', 'success');
                  passwordForm.reset();
              } else {
                  showMessage(data.message || 'Ошибка изменения пароля', 'error');
              }
          }).catch(() => showMessage('Ошибка изменения пароля', 'error'));
    });
}

// Удаление привычки
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const habitId = btn.getAttribute('data-habit-id');
        if (confirm('Вы уверены?')) {
            fetch(`/habits/delete/${habitId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json())
              .then(data => {
                  if (data.status === 'success') {
                      btn.closest('.habit-card').remove();
                      showMessage('Привычка удалена', 'success');
                  } else {
                      showMessage(data.message || 'Ошибка удаления', 'error');
                  }
              }).catch(() => showMessage('Ошибка удаления', 'error'));
        }
    });
});

// Вспомогательные функции
function closeModal() {
    settingsModal.style.display = 'none';
}

function showMessage(text, type) {
    const oldMsg = document.querySelector('.alert-message');
    if (oldMsg) oldMsg.remove();

    const msg = document.createElement('div');
    msg.className = `alert-message ${type}`;
    msg.innerHTML = text;
    document.body.appendChild(msg);

    setTimeout(() => {
        msg.classList.add('fade-out');
        setTimeout(() => msg.remove(), 500);
    }, 3000);
}

function showError(input, errorDiv, message) {
    input.classList.add('is-invalid');
    errorDiv.innerHTML = message;
    errorDiv.style.display = 'block';
}

function clearError(input, errorDiv) {
    input.classList.remove('is-invalid');
    errorDiv.innerHTML = '';
    errorDiv.style.display = 'none';
}

function getCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';')[0]);
}