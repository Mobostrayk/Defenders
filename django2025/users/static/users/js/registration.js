
    // Переключение темы
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // Функция для переключения видимости пароля
    function togglePasswordVisibility(fieldId) {
        const passwordField = document.getElementById(fieldId);
        const eyeIcon = document.getElementById(`eye-icon-${fieldId}`);

        if (passwordField.type === "password") {
            passwordField.type = "text";
            eyeIcon.innerHTML = `<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>`;
        } else {
            passwordField.type = "password";
            eyeIcon.innerHTML = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>`;
        }
    }

                // Получаем поле email
    const emailField = document.getElementById('{{ form.email.id_for_label }}');

    // Создаем элемент для отображения ошибки
    const emailError = document.createElement('div');
    emailError.className = 'invalid-feedback';
    emailField.parentNode.appendChild(emailError);

    // Обработчик ввода email
    emailField.addEventListener('input', function() {
        const email = this.value.trim();

        // Сбрасываем состояние ошибки
        this.classList.remove('is-invalid');
        emailError.style.display = 'none';

        // Не проверяем пустые значения
        if (!email) return;

        // Проверяем email на сервере
        fetch(`/check_email/?email=${encodeURIComponent(email)}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    this.classList.add('is-invalid');
                    emailError.textContent = 'Этот email уже зарегистрирован';
                    emailError.style.display = 'block';
                }
            })
            .catch(error => console.error('Ошибка:', error));
    });
    // Запрещенные логины
    const FORBIDDEN_USERNAMES = ['admin', 'administrator', 'root', 'moderator', 'support', 'superuser'];

    // Распространенные пароли
    const COMMON_PASSWORDS = [
        '123456', 'password', '12345678', 'qwerty', '123456789',
        '12345', '1234', '111111', '1234567', 'dragon',
        '123123', 'baseball', 'abc123', 'football', 'monkey'
    ];

    // Проверка запрещенных логинов
    function checkForbiddenUsernames() {
        const usernameField = document.getElementById('{{ form.username.id_for_label }}');
        const username = usernameField.value.trim().toLowerCase();
        const usernameError = document.getElementById('username-error');

        const isForbidden = FORBIDDEN_USERNAMES.some(word => username.includes(word));

        if (isForbidden) {
            usernameField.classList.add('is-invalid');
            usernameError.textContent = 'Этот логин запрещен для использования';
            usernameError.style.display = 'block';
            return false;
        }

        // Минимальная длина логина
        if (username.length > 0 && username.length < 3) {
            usernameField.classList.add('is-invalid');
            usernameError.textContent = 'Логин должен содержать минимум 3 символа';
            usernameError.style.display = 'block';
            return false;
        }

        usernameField.classList.remove('is-invalid');
        usernameError.style.display = 'none';
        return true;
    }

    // Проверка сложности пароля
    function checkPasswordStrength() {
        const passwordField = document.getElementById('{{ form.password1.id_for_label }}');
        const password = passwordField.value;
        const passwordError = document.getElementById('password-error');

        // Сбрасываем состояние ошибки
        passwordField.classList.remove('is-invalid', 'is-valid');
        passwordError.style.display = 'none';

        // Не показываем ошибки для пустого поля
        if (password.length === 0) {
            return true;
        }

        // Проверка на минимальную длину
        if (password.length < 8) {
            passwordField.classList.add('is-invalid');
            passwordError.textContent = 'Пароль должен содержать минимум 8 символов';
            passwordError.style.display = 'block';
            return false;
        }

        // Проверка на заглавные буквы
        if (!/[A-Z]/.test(password)) {
            passwordField.classList.add('is-invalid');
            passwordError.textContent = 'Пароль должен содержать хотя бы одну заглавную букву';
            passwordError.style.display = 'block';
            return false;
        }

        // Проверка на цифры
        if (!/[0-9]/.test(password)) {
            passwordField.classList.add('is-invalid');
            passwordError.textContent = 'Пароль должен содержать хотя бы одну цифру';
            passwordError.style.display = 'block';
            return false;
        }

        // Проверка на распространенность (только при отправке формы)
        if (COMMON_PASSWORDS.includes(password.toLowerCase())) {
            passwordField.classList.add('is-invalid');
            passwordError.textContent = 'Введённый пароль слишком широко распространён';
            passwordError.style.display = 'block';
            return false;
        }

        passwordField.classList.add('is-valid');
        return true;
    }

    // Проверка совпадения паролей
    function checkPasswordMatch() {
        const password1 = document.getElementById('{{ form.password1.id_for_label }}').value;
        const password2Field = document.getElementById('{{ form.password2.id_for_label }}');
        const password2Error = document.getElementById('password2-error');

        if (password1 !== password2Field.value) {
            password2Field.classList.add('is-invalid');
            password2Error.textContent = 'Пароли не совпадают';
            password2Error.style.display = 'block';
            return false;
        }

        password2Field.classList.remove('is-invalid');
        password2Field.classList.add('is-valid');
        password2Error.style.display = 'none';
        return true;
    }

    // Инициализация обработчиков событий
    document.addEventListener('DOMContentLoaded', function() {
        const usernameField = document.getElementById('{{ form.username.id_for_label }}');
        const password1Field = document.getElementById('{{ form.password1.id_for_label }}');
        const password2Field = document.getElementById('{{ form.password2.id_for_label }}');
        const form = document.getElementById('registration-form');

        // Обработчики для кнопок переключения видимости пароля
        document.querySelectorAll('.toggle-password').forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                togglePasswordVisibility(targetId);
            });
        });

        // Проверка логина на запрещенные слова при вводе
        usernameField.addEventListener('input', checkForbiddenUsernames);

        // Проверка пароля при вводе (без проверки на распространенность)
        password1Field.addEventListener('input', function() {
            const password = this.value;
            const passwordError = document.getElementById('password-error');

            // Сбрасываем состояние ошибки
            this.classList.remove('is-invalid', 'is-valid');
            passwordError.style.display = 'none';

            if (password.length === 0) return;

            if (password.length < 8) {
                this.classList.add('is-invalid');
                passwordError.textContent = 'Пароль должен содержать минимум 8 символов';
                passwordError.style.display = 'block';
            } else if (!/[A-Z]/.test(password)) {
                this.classList.add('is-invalid');
                passwordError.textContent = 'Пароль должен содержать хотя бы одну заглавную букву';
                passwordError.style.display = 'block';
            } else if (!/[0-9]/.test(password)) {
                this.classList.add('is-invalid');
                passwordError.textContent = 'Пароль должен содержать хотя бы одну цифру';
                passwordError.style.display = 'block';
            } else {
                this.classList.add('is-valid');
            }
        });

        // Проверка совпадения паролей при вводе
        password2Field.addEventListener('input', checkPasswordMatch);

        // Валидация перед отправкой формы
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const isUsernameValid = checkForbiddenUsernames();
            const isPasswordValid = checkPasswordStrength(); // Теперь включает проверку на распространенность
            const isPasswordMatch = checkPasswordMatch();

            if (!isUsernameValid || !isPasswordValid || !isPasswordMatch) {
                return;
            }

            // Проверка существования пользователя только при отправке формы
            const username = usernameField.value.trim();
            const usernameError = document.getElementById('username-error');

            try {
                const response = await fetch('/check_username/?username=' + encodeURIComponent(username));
                const data = await response.json();

                if (data.exists) {
                    usernameField.classList.add('is-invalid');
                    usernameError.textContent = 'Этот логин уже занят';
                    usernameError.style.display = 'block';
                    return;
                }

                // Если все проверки пройдены, отправляем форму
                form.submit();
            } catch (error) {
                console.error('Ошибка при проверке имени пользователя:', error);
                form.submit();
            }
        });
    });
