// WebSocket Chat Client
class WebSocketChat {
    constructor() {
        this.ws = null;
        this.messageCounter = 0;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000; // ms

        this.initializeElements();
        this.initializeEventListeners();
        this.connectWebSocket();
    }

    initializeElements() {
        this.form = document.getElementById('message-form');
        this.input = document.getElementById('message-input');
        this.statusText = document.getElementById('status-text');
        this.statusDot = document.querySelector('.status-dot');
        this.messagesList = document.getElementById('messages-list');
        this.sendBtn = document.getElementById('send-btn');
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    connectWebSocket() {
        const wsUrl = this.getWebSocketUrl();
        console.log(`Подключение к WebSocket: ${wsUrl}`);

        this.ws = new WebSocket(wsUrl);
        this.updateStatus('connecting', 'Подключение...');

        this.ws.onopen = () => this.handleOpen();
        this.ws.onmessage = (event) => this.handleMessage(event);
        this.ws.onerror = (error) => this.handleError(error);
        this.ws.onclose = (event) => this.handleClose(event);
    }

    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws`;
    }

    handleOpen() {
        console.log('WebSocket подключен');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateStatus('connected', 'Подключено');
    }

    handleMessage(event) {
        console.log('Получено сообщение:', event.data);

        try {
            const data = JSON.parse(event.data);

            if (data.type === 'message') {
                this.addMessageToList(data.id, data.text);
            } else if (data.type === 'error') {
                this.showError(data.message);
            }
        } catch (error) {
            console.error('Ошибка обработки сообщения:', error);
        }
    }

    handleError(error) {
        console.error('WebSocket ошибка:', error);
        this.updateStatus('error', 'Ошибка подключения');
    }

    handleClose(event) {
        console.log('WebSocket отключен:', event.code, event.reason);
        this.isConnected = false;
        this.updateStatus('disconnected', 'Отключено');

        // Пытаемся переподключиться
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;
            console.log(`Переподключение через ${delay}ms (попытка ${this.reconnectAttempts})`);

            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            this.updateStatus('failed', 'Не удалось подключиться');
        }
    }

    handleSubmit(e) {
        e.preventDefault();

        const message = this.input.value.trim();
        if (!message) {
            this.showError('Введите сообщение');
            return;
        }

        if (!this.isConnected) {
            this.showError('Нет подключения к серверу');
            return;
        }

        this.sendMessage(message);
        this.input.value = '';
    }

    sendMessage(text) {
        const message = {
            text: text,
            timestamp: new Date().toISOString()
        };

        try {
            this.ws.send(JSON.stringify(message));
            console.log('Отправлено сообщение:', message);
        } catch (error) {
            console.error('Ошибка отправки:', error);
            this.showError('Ошибка отправки сообщения');
        }
    }

    addMessageToList(id, text) {
        const emptyState = this.messagesList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }

        const messageElement = document.createElement('div');
        messageElement.className = 'message-item';

        // Более компактный формат времени
        const time = new Date();
        const timeStr = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;

        messageElement.innerHTML = `
            <div class="message-header">
                <span class="message-id">#${id}</span>
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-text">${this.escapeHtml(text)}</div>
        `;

        this.messagesList.prepend(messageElement);
    }

    showError(message) {
        console.error('Ошибка:', message);

        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = `Ошибка: ${message}`;
        errorElement.style.cssText = `
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #c00;
        `;

        // Показываем ошибку на 5 секунд
        this.messagesList.prepend(errorElement);
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.remove();
            }
        }, 5000);
    }

    updateStatus(status, text) {
        this.statusText.textContent = text;

        const colors = {
            connecting: '#ffd700', // желтый
            connected: '#28a745',  // зеленый
            disconnected: '#dc3545', // красный
            error: '#dc3545',
            failed: '#6c757d' // серый
        };

        this.statusDot.style.backgroundColor = colors[status] || '#6c757d';

        // Останавливаем анимацию пульса при подключении
        if (status === 'connected') {
            this.statusDot.style.animation = 'none';
        } else {
            this.statusDot.style.animation = 'pulse 2s infinite';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.chat = new WebSocketChat();
});