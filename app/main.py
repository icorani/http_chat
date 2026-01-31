from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="WebSocket Chat API",
    description="Реализация чата с WebSocket и нумерацией сообщений",
    version="1.0.0"
)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static/"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Основная страница приложения"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Chat</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>🚀 WebSocket Chat</h1>
            <div class="status-card">
                <p>✅ Сервер успешно запущен!</p>
                <p>📚 Документация API: <a href="/docs" target="_blank">/docs</a></p>
                <p>📊 Альтернативная документация: <a href="/redoc" target="_blank">/redoc</a></p>
            </div>
            <div class="next-steps">
                <h2>Следующие шаги:</h2>
                <ol>
                    <li>Добавить HTML форму для сообщений</li>
                    <li>Реализовать WebSocket endpoint</li>
                    <li>Добавить нумерацию сообщений</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """