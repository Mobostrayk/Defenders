document.addEventListener('DOMContentLoaded', function() {
    // Таймер обратного отсчета
    function startTimer(duration, display) {
        let timer = duration, minutes, seconds;
        const interval = setInterval(function () {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            display.textContent = "Код действителен еще: " + minutes + ":" + seconds;

            if (--timer < 0) {
                clearInterval(interval);
                display.textContent = "Срок действия кода истек";
            }
        }, 1000);
    }

    const timerDisplay = document.querySelector('.text-muted.small');
    if (timerDisplay) {
        startTimer(300, timerDisplay); // 5 минут = 300 секунд
    }

    // Обработчик повторной отправки
    const resendBtn = document.getElementById('resend-btn');
    if (resendBtn) {
        resendBtn.addEventListener('click', function(e) {
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
                    alert('Новый код отправлен!');
                    if (timerDisplay) {
                        startTimer(300, timerDisplay);
                    }
                } else {
                    alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
                }
            });
        });
    }
});