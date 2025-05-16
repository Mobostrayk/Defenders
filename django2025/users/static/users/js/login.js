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

        // Инициализация обработчиков событий
        document.addEventListener('DOMContentLoaded', function() {
            // Обработчики для кнопок переключения видимости пароля
            document.querySelectorAll('.toggle-password').forEach(button => {
                button.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target');
                    togglePasswordVisibility(targetId);
                });
            });

            // Валидация формы авторизации
            const loginForm = document.getElementById('login-form');
            if (loginForm) {
                loginForm.addEventListener('submit', function(e) {
                    const usernameField = document.getElementById('{{ form.username.id_for_label }}');
                    const passwordField = document.getElementById('{{ form.password.id_for_label }}');
                    let isValid = true;

                    // Сброс ошибок
                    usernameField.classList.remove('is-invalid');
                    passwordField.classList.remove('is-invalid');
                    document.getElementById('username-error').style.display = 'none';
                    document.getElementById('password-error').style.display = 'none';

                    // Проверка имени пользователя
                    if (!usernameField.value.trim()) {
                        usernameField.classList.add('is-invalid');
                        document.getElementById('username-error').textContent = 'Введите имя пользователя';
                        document.getElementById('username-error').style.display = 'block';
                        isValid = false;
                    }

                    // Проверка пароля
                    if (!passwordField.value) {
                        passwordField.classList.add('is-invalid');
                        document.getElementById('password-error').textContent = 'Введите пароль';
                        document.getElementById('password-error').style.display = 'block';
                        isValid = false;
                    }

                    if (!isValid) {
                        e.preventDefault();
                        // Прокручиваем к первой ошибке
                        const firstError = document.querySelector('.is-invalid');
                        if (firstError) {
                            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }

                    const captchaResponse = grecaptcha.getResponse();
                    if (!captchaResponse) {
                        e.preventDefault();
                        alert('Пожалуйста, подтвердите что вы не робот');
                        return;
                        });
            }
        });