// app/static/app.js
console.log('WebSocket Chat loaded');

// Базовые обработчики формы
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('message-form');
    const input = document.getElementById('message-input');
    const statusText = document.getElementById('status-text');
    const sendBtn = document.getElementById('send-btn');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = input.value.trim();

        if (message) {
            console.log('Отправка сообщения:', message);
            input.value = '';
            // TODO: WebSocket отправка
        }
    });

    // TODO: WebSocket подключение
    statusText.textContent = 'Готов к подключению WebSocket';
});