from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="WebSocket Chat API",
    description="Чат с WebSocket и нумерацией сообщений",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chat</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>💬 WebSocket Chat</h1>

        <div class="status">
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span id="status-text">Подключение...</span>
            </div>
        </div>

        <div class="chat-wrapper">
            <div class="messages-panel">
                <h2>📨 Сообщения</h2>
                <div class="messages-list" id="messages-list">
                    <div class="empty-state">Сообщений пока нет</div>
                </div>
            </div>

            <div class="form-panel">
                <h2>✏️ Новое сообщение</h2>
                <form id="message-form">
                    <textarea 
                        id="message-input" 
                        placeholder="Введите сообщение..." 
                        rows="4"
                        required
                    ></textarea>
                    <button type="submit" id="send-btn">Отправить</button>
                </form>
            </div>
        </div>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>
    """