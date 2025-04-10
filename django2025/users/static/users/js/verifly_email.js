
document.getElementById('resend-btn').addEventListener('click', function() {
    const btn = this;
    const email = btn.dataset.email;
    const timer = document.getElementById('timer');

    btn.disabled = true;

    fetch('/resend-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: `email=${encodeURIComponent(email)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Запускаем таймер
            let seconds = 60;
            timer.style.display = 'inline';
            timer.textContent = `(До следующей отправки: ${seconds} сек)`;

            const interval = setInterval(() => {
                seconds--;
                timer.textContent = `(До следующей отправки: ${seconds} сек)`;

                if (seconds <= 0) {
                    clearInterval(interval);
                    timer.style.display = 'none';
                    btn.disabled = false;
                }
            }, 1000);
        } else {
            alert(data.error || 'Ошибка отправки');
            btn.disabled = false;
        }
    });
});
