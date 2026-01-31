from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="WebSocket Chat API",
    description="Чат с WebSocket и нумерацией сообщений",
    version="1.0.0"
)

# Статика (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory="static/"), name="static")

# Главная страница - отдаем index.html из статики
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# Документация API доступна по /docs и /redoc автоматически
