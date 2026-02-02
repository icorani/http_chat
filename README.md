# WebSocket Chat - FastAPI + JavaScript

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-实时通信-yellow?logo=websocket&logoColor=white)

Реализация веб-чата с использованием WebSocket, FastAPI и чистого JavaScript. Сообщения автоматически нумеруются начиная с 1, нумерация сбрасывается при перезагрузке страницы.

## Особенности

- Обмен сообщениями через WebSocket
- Автоматическая нумерация сообщений (с 1)
- Сброс нумерации при перезагрузке страницы
- JSON формат обмена данными
- Динамическое обновление без перезагрузки
- Автоматическое переподключение при потере связи
- Приложение упаковано в Docker

## Структура проекта
```
websocket-chat/
├── app/                          # Основное приложение
│   ├── __init__.py
│   ├── main.py                   # FastAPI приложение + WebSocket
│   └── static/                   # Статические файлы
│       ├── index.html            # HTML страница чата
│       ├── style.css             # CSS стили
│       └── app.js                # JavaScript логика
├── start_server.py               # Скрипт запуска сервера
├── requirements.txt              # Python зависимости
├── Dockerfile                    # Docker образ
├── docker-compose.yml            # Docker Compose конфигурация
├── .dockerignore                 # Игнорируемые файлы для Docker
├── .gitignore                    # Игнорируемые файлы для Git
└── README.md                     # Документация
```

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
python start_server.py
```
Сервер запустится на http://localhost:6088

### 3. API Endpoints
[GET /](http://localhost:6088) - Главная страница чата

[GET /docs](http://localhost:6088/docs) - Документация Swagger UI

[GET /redoc](http://localhost:6088/redoc) - Альтернативная документация

[GET /health](http://localhost:6088/health) - Health check

[GET /ws-info](http://localhost:6088/ws-info) - Статус WebSocket соединений

[WS /ws](http://localhost:6088/ws) - WebSocket endpoint для чата

### 4. Сборка и запуск Docker

```bash
# Сборка образа
docker build -t websocket-chat .

# Запуск контейнера
docker run -d -p 8000:8000 --name websocket-chat websocket-chat

# Или через docker-compose
docker-compose up -d
