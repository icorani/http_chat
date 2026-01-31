# WebSocket Chat - FastAPI + JavaScript

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-实时通信-yellow?logo=websocket&logoColor=white)

Реализация веб-чата с использованием WebSocket, FastAPI и чистого JavaScript. Сообщения автоматически нумеруются начиная с 1, нумерация сбрасывается при перезагрузке страницы.

## Особенности

- Real-time обмен сообщениями через WebSocket
- Автоматическая нумерация сообщений (с 1)
- Сброс нумерации при перезагрузке страницы
- JSON формат обмена данными
- Динамическое обновление без перезагрузки
- Автоматическое переподключение при потере связи
- Современный минималистичный UI

## Структура проекта
websocket-chat/
├── app/
│ ├── main.py # FastAPI приложение + WebSocket
│ └── static/
│ ├── index.html # HTML страница
│ ├── style.css # Стили
│ └── app.js # JavaScript логика
├── run.py # Скрипт запуска
├── requirements.txt # Зависимости Python
└── README.md

## Быстрый старт

### 1. Установка зависимостей

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd websocket-chat

# Создать виртуальное окружение
python -m venv venv

# Активировать (Linux/Mac)
source venv/bin/activate

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```
### 2. Запуск сервера
```bash
python run.py
```
Сервер запустится на http://localhost:6088

### 3. API Endpoints
![GET /](http://localhost:6088) - Главная страница чата

![GET /docs](http://localhost:6088/docs) - Документация Swagger UI

![GET /redoc](http://localhost:6088/redoc) - Альтернативная документация

![GET /health](http://localhost:6088/health) - Health check

![GET /ws-info](http://localhost:6088/ws-info) - Статус WebSocket соединений

![WS /ws](http://localhost:6088/ws) - WebSocket endpoint для чата

