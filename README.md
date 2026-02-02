# WebSocket Chat - FastAPI + JavaScript

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-实时通信-yellow?logo=websocket&logoColor=white)

Реализация веб-чата с использованием WebSocket, FastAPI и чистого JavaScript. Сообщения автоматически нумеруются начиная с 1, нумерация сбрасывается при перезагрузке страницы.

### 1. Особенности

- Обмен сообщениями через WebSocket
- Автоматическая нумерация сообщений отправленных клиентом
- Итентификация клиентов по UUID
- Сброс нумерации сообщений при обновлении страницы
- После обновления/открытия страницы клиент считается подключившимся зановоно. Новый UUID
- JSON формат обмена данными
- Динамическое обновление без перезагрузки
- Автоматическое переподключение при потере связи
- Приложение упаковано в Docker, запуск через docker compose

### 2. Структура проекта
```
http_chat/                  # Корень проекта
├── app/                    # Основное приложение
│   ├── static/             # Статические файлы
│   │   ├── app.js          # JavaScript фронтенд
│   │   ├── index.html      # HTML интерфейс чата
│   │   └── style.css       # CSS стили
│   ├── __init__.py         # Пакет app
│   ├── connection_manager.py # Менеджер WebSocket соединений
│   ├── database.py         # Настройка и подключение к БД
│   ├── main.py             # Основной FastAPI application
│   ├── models.py           # SQLAlchemy модели БД
│   └── schemas.py          # Pydantic схемы для валидации
├── .dockerignore           # Исключения для Docker
├── .gitignore              # Исключения для Git
├── docker-compose.yaml     # Docker Compose конфигурация
├── Dockerfile              # Docker образ приложения
├── README.md               # Документация проекта
├── requirements.txt        # Зависимости Python
└── start_server.py         # Скрипт запуска сервера
```


### 3. Запуск сервера через Docker Compose
Порт для сервера в переменных окружения docker compose
Также в переменных статус определяется DEBUG 
При запуске поднимается uvicorn server для FastAPI приложения и postgres сервер для хранения данных.

```bash
# Запуск через docker-compose
docker compose up -d --build
```

### 4. API Endpoints
[GET /](http://localhost:6088) - Главная страница чата

[GET /docs](http://localhost:6088/docs) - Документация Swagger UI

[GET /redoc](http://localhost:6088/redoc) - Альтернативная документация

[GET /health](http://localhost:6088/health) - Health check

[GET /ws-info](http://localhost:6088/ws-info) - Статус WebSocket соединений

[WS /ws](http://localhost:6088/ws) - WebSocket endpoint для чата


### 5. Запуск в окружении через start_server.
Необходимо установить зависимости, при необходимости задать переменные окружения, обеспечить корректное подключение к БД.
Дефолтные настройки:
- HOST = "0.0.0.0"
- PORT = "6088"
- DEBUG = "false"
- DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/websocket_chat"
