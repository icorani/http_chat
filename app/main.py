from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import logging

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("websocket_chat")

app = FastAPI(
    title="WebSocket Chat API",
    description="Чат с WebSocket и нумерацией сообщений",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class ConnectionManager:
    """
    Connection manager for WebSocket connections.

    Manages active connections, message numbering, and message distribution.

    Attributes:
        active_connections: List of active WebSocket connections
        message_counter: Sequential message ID counter

    Methods:
        connect(websocket: WebSocket) -> None:
            Accept new WebSocket connection
        disconnect(websocket: WebSocket) -> None:
            Remove WebSocket connection
        get_next_message_id() -> int:
            Get next sequential message ID
        send_personal_message(message: str, websocket: WebSocket) -> None:
            Send message to specific client
        broadcast(message: str) -> None:
            Broadcast message to all connected clients
    """
    def __init__(self):
        self.active_connections = []
        self.message_counter = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Новое подключение WebSocket. Всего: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Отключение WebSocket. Осталось: {len(self.active_connections)}")

    def get_next_message_id(self):
        self.message_counter += 1
        logger.debug(f"Сгенерирован ID сообщения: {self.message_counter}")
        return self.message_counter

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            logger.debug(f"Отправлено персональное сообщение")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")

    async def broadcast(self, message: str):
        successful = 0
        failed = 0
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                successful += 1
            except Exception as e:
                failed += 1
                logger.warning(f"Не удалось отправить broadcast: {e}")
        if successful > 0 or failed > 0:
            logger.info(f"Broadcast: успешно {successful}, неудачно {failed}")


manager = ConnectionManager()


@app.get("/")
async def read_root():
    logger.debug("Запрос главной страницы")
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"Инициализация WebSocket соединения от {client_ip}")

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Получены данные от {client_ip}: {data[:50]}...")

            try:
                message_data = json.loads(data)
                text = message_data.get("text", "").strip()

                if not text:
                    logger.warning(f"Пустое сообщение от {client_ip}")
                    error_response = {
                        "type": "error",
                        "message": "Message text cannot be empty"
                    }
                    await manager.send_personal_message(
                        json.dumps(error_response),
                        websocket
                    )
                    continue

                message_id = manager.get_next_message_id()
                response = {
                    "id": message_id,
                    "text": text,
                    "type": "message"
                }

                response_json = json.dumps(response)
                await manager.send_personal_message(response_json, websocket)
                logger.info(f"Отправлен ответ {client_ip}: ID={message_id}, текст={text[:30]}...")

            except json.JSONDecodeError as e:
                logger.error(f"Невалидный JSON от {client_ip}: {e}")
                error_response = {
                    "type": "error",
                    "message": f"Invalid JSON: {str(e)}"
                }
                await manager.send_personal_message(
                    json.dumps(error_response),
                    websocket
                )
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения от {client_ip}: {e}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket отключен: {client_ip}")
        manager.disconnect(websocket)
        manager.message_counter = 0
        logger.info("Счетчик сообщений сброшен для новой сессии")
    except Exception as e:
        logger.error(f"Неожиданная ошибка WebSocket: {e}")
        manager.disconnect(websocket)


@app.get("/ws-info")
async def websocket_info():
    info = {
        "active_connections": len(manager.active_connections),
        "message_counter": manager.message_counter,
        "status": "running"
    }
    logger.debug(f"Запрос информации о WebSocket: {info}")
    return info


@app.get("/health")
async def health_check():
    logger.debug("Health check запрос")
    return {"status": "healthy", "service": "websocket-chat"}