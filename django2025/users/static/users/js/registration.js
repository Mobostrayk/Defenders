
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
    // 1. Получаем элементы формы
    const form = document.getElementById('registration-form');
    if (!form) return;

    // 2. Находим поля по стандартным Django ID
    const fields = {
        username: document.getElementById('id_username'),
        email: document.getElementById('id_email'),
        password1: document.getElementById('id_password1'),
        password2: document.getElementById('id_password2')
    };

    // 3. Создаем контейнеры для ошибок
    const errorContainers = {
        username: document.getElementById('username-error') || createErrorElement(fields.username),
        email: document.getElementById('email-error') || createErrorElement(fields.email),
        password1: document.getElementById('password-error') || createErrorElement(fields.password1),
        password2: document.getElementById('password2-error') || createErrorElement(fields.password2)
    };

    // 4. Константы валидации
    const FORBIDDEN_USERNAMES = ['admin', 'administrator', 'root'];
    const COMMON_PASSWORDS = ['123456', 'password', 'qwerty'];

    // 5. Инициализация
    initPasswordToggle();
    initValidation();

    // ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

    function createErrorElement(field) {
        if (!field || !field.parentNode) return null;
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
        return errorElement;
    }

    function initPasswordToggle() {
        document.querySelectorAll('.toggle-password').forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const passwordField = document.getElementById(targetId);
                const eyeIcon = document.getElementById(`eye-icon-${targetId}`);
                
                if (passwordField && eyeIcon) {
                    passwordField.type = passwordField.type === 'password' ? 'text' : 'password';
                    eyeIcon.innerHTML = passwordField.type === 'password' 
                        ? '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>'
                        : '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
                }
            });
        });
    }

    function initValidation() {
        // Валидация в реальном времени
        if (fields.username) fields.username.addEventListener('input', validateUsername);
        if (fields.email) fields.email.addEventListener('input', validateEmail);
        if (fields.password1) fields.password1.addEventListener('input', validatePassword);
        if (fields.password2) fields.password2.addEventListener('input', validatePasswordConfirm);

        // Обработка отправки формы
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const isFormValid = [
                validateUsername(),
                validateEmail(),
                validatePassword(),
                validatePasswordConfirm(),
                await checkUsernameAvailability()
            ].every(valid => valid);

            if (isFormValid) form.submit();
        });
    }

    // ===== ФУНКЦИИ ВАЛИДАЦИИ =====

    function validateUsername() {
        const value = fields.username.value.trim();
        const error = errorContainers.username;
        
        if (!value) return true;

        if (FORBIDDEN_USERNAMES.some(name => value.toLowerCase().includes(name))) {
            showError(fields.username, error, 'Этот логин запрещен');
            return false;
        }

        if (value.length < 3) {
            showError(fields.username, error, 'Минимум 3 символа');
            return false;
        }

        clearError(fields.username, error);
        return true;
    }

    function validateEmail() {
        const value = fields.email.value.trim();
        const error = errorContainers.email;
        
        if (!value) return true;

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            showError(fields.email, error, 'Некорректный email');
            return false;
        }

        // Проверка на сервере
        fetch(`/check_email/?email=${encodeURIComponent(value)}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) showError(fields.email, error, 'Email уже занят');
            });

        clearError(fields.email, error);
        return true;
    }

    function validatePassword() {
        const value = fields.password1.value;
        const error = errorContainers.password1;
        
        if (!value) return true;

        if (value.length < 8) {
            showError(fields.password1, error, 'Минимум 8 символов');
            return false;
        }

        if (!/[A-Z]/.test(value)) {
            showError(fields.password1, error, 'Добавьте заглавную букву');
            return false;
        }

        if (COMMON_PASSWORDS.includes(value.toLowerCase())) {
            showError(fields.password1, error, 'Слишком простой пароль');
            return false;
        }

        clearError(fields.password1, error);
        return true;
    }

    function validatePasswordConfirm() {
        const value = fields.password2.value;
        const error = errorContainers.password2;
        
        if (value !== fields.password1.value) {
            showError(fields.password2, error, 'Пароли не совпадают');
            return false;
        }

        clearError(fields.password2, error);
        return true;
    }

    async function checkUsernameAvailability() {
        const value = fields.username.value.trim();
        const error = errorContainers.username;
        
        try {
            const response = await fetch(`/check_username/?username=${encodeURIComponent(value)}`);
            const data = await response.json();
            
            if (data.exists) {
                showError(fields.username, error, 'Логин уже занят');
                return false;
            }
            return true;
        } catch (e) {
            console.error('Ошибка проверки логина:', e);
            return true; // Пропускаем ошибку сети
        }
    }

    function showError(field, errorElement, message) {
        if (!field || !errorElement) return;
        field.classList.add('is-invalid');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    function clearError(field, errorElement) {
        if (!field || !errorElement) return;
        field.classList.remove('is-invalid');
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
});