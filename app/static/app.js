// WebSocket Chat Client (без localStorage, с нумерацией от сервера)
class WebSocketChat {
    constructor() {
        this.ws = null;
        this.connectionId = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        
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
        console.log('WebSocket подключен, ожидаем инициализации от сервера...');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateStatus('connected', 'Подключено (ожидание данных...)');
    }
    
    handleMessage(event) {
        console.log('Получено сообщение от сервера:', event.data);
        
        try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'init':
                    this.handleInit(data);
                    break;
                case 'message':
                    this.handleNewMessage(data);
                    break;
                case 'history':
                    this.handleHistory(data.messages);
                    break;
                case 'error':
                    this.showError(data.message);
                    break;
                default:
                    console.warn('Неизвестный тип сообщения:', data.type);
            }
        } catch (error) {
            console.error('Ошибка обработки сообщения:', error, event.data);
        }
    }
    
    handleInit(data) {
        this.connectionId = data.connection_id;
        console.log(`Инициализация. Connection ID: ${this.connectionId}`);
        
        this.updateStatus('connected', 'Подключено');
        
        // Очищаем список сообщений перед загрузкой истории
        this.clearMessagesList();
        
        // Загружаем историю сообщений
        if (data.history && data.history.length > 0) {
            this.handleHistory(data.history);
        }
    }
    
    handleHistory(messages) {
        console.log(`Загружаем историю: ${messages.length} сообщений`);
        
        // Сортируем по времени (старые -> новые) для правильного отображения
        const sortedMessages = [...messages].sort((a, b) => 
            new Date(a.created_at) - new Date(b.created_at)
        );
        
        // Отображаем каждое сообщение
        sortedMessages.forEach(msg => {
            this.addMessageToDOM({
                text: msg.text,
                connectionId: msg.connection_id,
                messageNumber: msg.user_message_number,
                isOwn: msg.connection_id === this.connectionId,
                timestamp: msg.created_at || new Date().toISOString()
            }, false);
        });
        
        // Прокручиваем к последнему сообщению
        this.scrollToBottom();
    }
    
    handleNewMessage(data) {
        console.log('Новое сообщение:', data);
        
        this.addMessageToDOM({
            text: data.text,
            connectionId: data.connection_id,
            messageNumber: data.user_message_number,
            isOwn: data.connection_id === this.connectionId,
            timestamp: data.created_at || new Date().toISOString()
        }, true);
        
        // Обновляем счетчик сообщений если есть
        this.updateMessageCount();
    }
    
    handleError(error) {
        console.error('WebSocket ошибка:', error);
        this.updateStatus('error', 'Ошибка подключения');
    }
    
    handleClose(event) {
        console.log('WebSocket отключен:', event.code, event.reason);
        this.isConnected = false;
        this.connectionId = null;
        this.updateStatus('disconnected', 'Отключено');
        
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
        
        if (!this.connectionId) {
            this.showError('Ожидаем инициализацию от сервера');
            return;
        }
        
        this.sendMessage(message);
        this.input.value = '';
        this.input.focus();
    }
    
    sendMessage(text) {
        const message = {
            type: 'message',
            text: text
        };
        
        try {
            this.ws.send(JSON.stringify(message));
            console.log('Отправлено сообщение:', message);
        } catch (error) {
            console.error('Ошибка отправки:', error);
            this.showError('Ошибка отправки сообщения');
        }
    }
    
    addMessageToDOM(messageData, animate = true) {
        // Убираем состояние "пусто" если есть
        const emptyState = this.messagesList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message-item';
        
        // Добавляем класс для чужих сообщений
        if (!messageData.isOwn) {
            messageElement.classList.add('other-user');
        }
        
        if (animate) {
            messageElement.style.animation = 'slideIn 0.2s ease-out';
        }
        
        const time = new Date(messageData.timestamp);
        const timeStr = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;
        
        let headerHTML = '';
        if (messageData.isOwn && messageData.messageNumber) {
            headerHTML = `<span class="message-id">#${messageData.messageNumber}</span>`;
        } else if (!messageData.isOwn) {
            headerHTML = `<span class="user-label">${this.getUserLabel(messageData.connectionId)}</span>`;
        }
        
        messageElement.innerHTML = `
            <div class="message-header">
                ${headerHTML}
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-text">${this.escapeHtml(messageData.text)}</div>
        `;
        
        this.messagesList.appendChild(messageElement);
        
        // Прокручиваем к новому сообщению
        messageElement.scrollIntoView({ behavior: 'smooth' });
    }
    
    getUserLabel(connectionId) {
        // Создаем короткий идентификатор пользователя на основе connectionId
        if (!connectionId) return 'Аноним';
        const shortId = connectionId.substring(0, 6);
        return `Пользователь ${shortId}`;
    }
    
    clearMessagesList() {
        this.messagesList.innerHTML = '<div class="empty-state">Загрузка истории...</div>';
    }
    
    scrollToBottom() {
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }
    
    showError(message) {
        console.error('Ошибка:', message);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = `Ошибка: ${message}`;
        
        // Добавляем стили инлайн чтобы не зависеть от CSS
        errorElement.style.cssText = `
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #c00;
        `;
        
        // Вставляем ошибку в начало списка сообщений
        if (this.messagesList.firstChild) {
            this.messagesList.insertBefore(errorElement, this.messagesList.firstChild);
        } else {
            this.messagesList.appendChild(errorElement);
        }
        
        // Удаляем через 5 секунд
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.remove();
            }
        }, 5000);
    }
    
    updateStatus(status, text) {
        if (!this.statusText) return;
        
        this.statusText.textContent = text;
        
        const colors = {
            connecting: '#ffd700',
            connected: '#28a745',
            disconnected: '#dc3545',
            error: '#dc3545',
            failed: '#6c757d'
        };
        
        if (this.statusDot) {
            this.statusDot.style.backgroundColor = colors[status] || '#6c757d';
            
            if (status === 'connected') {
                this.statusDot.style.animation = 'none';
            } else {
                this.statusDot.style.animation = 'pulse 2s infinite';
            }
        }
    }
    
    updateMessageCount() {
        // Можно добавить счетчик сообщений если нужно
        const countElement = document.getElementById('message-count');
        if (countElement) {
            const messages = this.messagesList.querySelectorAll('.message-item');
            const myMessages = this.messagesList.querySelectorAll('.message-item:not(.other-user)');
            countElement.textContent = `${myMessages.length}/${messages.length}`;
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