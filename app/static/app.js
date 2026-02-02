// WebSocket Chat Client с поддержкой сессий и localStorage
class WebSocketChat {
    constructor() {
        this.ws = null;
        this.sessionId = this.generateSessionId();
        this.currentSessionMessages = 0;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        
        this.initializeElements();
        this.initializeStorage();
        this.initializeEventListeners();
        this.connectWebSocket();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeElements() {
        this.form = document.getElementById('message-form');
        this.input = document.getElementById('message-input');
        this.statusText = document.getElementById('status-text');
        this.statusDot = document.querySelector('.status-dot');
        this.messagesList = document.getElementById('messages-list');
        this.sendBtn = document.getElementById('send-btn');
    }
    
    initializeStorage() {
        const stored = localStorage.getItem('websocket_chat_data');
        if (stored) {
            try {
                this.storageData = JSON.parse(stored);
                if (this.storageData.currentSessionId !== this.sessionId) {
                    this.storageData.currentSessionId = this.sessionId;
                    this.saveToStorage();
                }
            } catch (e) {
                console.error('Ошибка чтения localStorage:', e);
                this.resetStorage();
            }
        } else {
            this.resetStorage();
        }
        
        this.loadMessageHistory();
    }
    
    resetStorage() {
        this.storageData = {
            currentSessionId: this.sessionId,
            messages: []
        };
        this.saveToStorage();
    }
    
    saveToStorage() {
        try {
            localStorage.setItem('websocket_chat_data', JSON.stringify(this.storageData));
        } catch (e) {
            console.error('Ошибка записи в localStorage:', e);
        }
    }
    
    loadMessageHistory() {
        const emptyState = this.messagesList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        this.storageData.messages.forEach(msg => {
            this.addMessageToDOM(msg, false);
        });
        
        this.currentSessionMessages = this.storageData.messages.filter(
            msg => msg.sessionId === this.sessionId
        ).length;
        
        this.updateMessageCount();
    }
    
    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        const clearBtn = document.getElementById('clear-history');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearHistory());
        }
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
        this.input.focus();
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
        this.currentSessionMessages++;
        
        const messageData = {
            text: text,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString(),
            messageNumber: this.currentSessionMessages
        };
        
        this.storageData.messages.push(messageData);
        this.saveToStorage();
        
        this.addMessageToDOM(messageData, true);
        this.updateMessageCount();
    }
    
    addMessageToDOM(messageData, animate = true) {
        const isCurrentSession = messageData.sessionId === this.sessionId;
        const hasNumber = isCurrentSession && messageData.messageNumber;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message-item';
        
        if (!isCurrentSession) {
            messageElement.classList.add('previous-session');
        }
        
        if (animate) {
            messageElement.style.animation = 'slideIn 0.2s ease-out';
        }
        
        const time = new Date(messageData.timestamp);
        const timeStr = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;
        
        let headerHTML = '';
        if (hasNumber) {
            headerHTML = `<span class="message-id">#${messageData.messageNumber}</span>`;
        } else if (!isCurrentSession) {
            headerHTML = `<span class="session-label">(предыдущая сессия)</span>`;
        }
        
        messageElement.innerHTML = `
            <div class="message-header">
                ${headerHTML}
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-text">${this.escapeHtml(messageData.text)}</div>
        `;
        
        this.messagesList.prepend(messageElement);
    }
    
    clearHistory() {
        if (confirm('Очистить всю историю сообщений?')) {
            this.resetStorage();
            this.messagesList.innerHTML = '<div class="empty-state">Сообщений пока нет</div>';
            this.currentSessionMessages = 0;
            this.updateMessageCount();
        }
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
            connecting: '#ffd700',
            connected: '#28a745',
            disconnected: '#dc3545',
            error: '#dc3545',
            failed: '#6c757d'
        };
        
        this.statusDot.style.backgroundColor = colors[status] || '#6c757d';
        
        if (status === 'connected') {
            this.statusDot.style.animation = 'none';
        } else {
            this.statusDot.style.animation = 'pulse 2s infinite';
        }
    }
    
    updateMessageCount() {
        const countElement = document.getElementById('message-count');
        if (countElement) {
            const currentCount = this.storageData.messages.filter(
                msg => msg.sessionId === this.sessionId
            ).length;
            countElement.textContent = currentCount;
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