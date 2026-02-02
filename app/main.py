"""
FastAPI WebSocket chat with message numbering per connection.
"""
import os
import json
import logging
from uuid import UUID
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db, init_db
from .connection_manager import ConnectionManager
from .schemas import MessageCreate, MessageResponse, InitResponse, ErrorResponse

logger = logging.getLogger("websocket_chat")
logger.setLevel(logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO)

static_path = os.path.join(os.path.dirname(__file__), "static")

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("🚀 Starting WebSocket chat")
    
    # ИНИЦИАЛИЗИРУЕМ БАЗУ ДАННЫХ ПЕРЕД ЗАПУСКОМ
    try:
        logger.info("📦 Initializing database...")
        success = await init_db()
        if not success:
            logger.error("❌ Failed to initialize database")
            raise RuntimeError("Database initialization failed")
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise
    
    yield
    
    logger.info("🛑 Stopping WebSocket chat")

app = FastAPI(
    title="WebSocket Chat API",
    description="Chat with WebSocket and per-connection message numbering",
    version="1.0.0",
    lifespan=lifespan
)

# Проверяем существование папки static перед монтированием
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info(f"✅ Static files mounted at {static_path}")
else:
    logger.warning(f"⚠️ Static directory not found: {static_path}")

@app.get("/")
async def read_root():
    """Serve chat interface."""
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        status_code=404,
        content={"error": "index.html not found"}
    )

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_status = True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        db_status = False
    
    return JSONResponse({
        "status": "healthy" if db_status else "degraded",
        "service": "websocket-chat",
        "database": db_status,
        "connections": manager.get_connection_count()
    })

@app.get("/ws-info")
async def websocket_info():
    """WebSocket connection information."""
    return {
        "active_connections": manager.get_connection_count(),
        "status": "running"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """
    WebSocket endpoint for chat.
    
    Each connection gets unique connection_id and separate message numbering.
    Numbering resets on reconnection.
    """
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"New WebSocket connection from {client_ip}")
    
    try:
        connection_id = await manager.connect(websocket)
        logger.info(f"Generated connection_id: {connection_id} for {client_ip}")
        
        history_messages = await manager.get_message_history(db, limit=50)
        
        init_data = InitResponse(
            connection_id=str(connection_id),
            history=[
                MessageResponse(
                    id=msg.id,
                    text=msg.text,
                    connection_id=str(msg.connection_id),
                    user_message_number=msg.user_message_number,
                    created_at=msg.created_at,
                )
                for msg in history_messages
            ]
        )
        await manager.send_personal_message(init_data.model_dump(), websocket)
        
        logger.info(f"Client {client_ip} initialized with {len(history_messages)} history messages")
        
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received message from {client_ip}: {data[:100]}...")
            
            try:
                message_data = json.loads(data)
                
                if "type" not in message_data:
                    error = ErrorResponse(message="Missing 'type' field")
                    await manager.send_personal_message(error.model_dump(), websocket)
                    continue
                
                if message_data["type"] != "message":
                    error = ErrorResponse(message=f"Unknown message type: {message_data['type']}")
                    await manager.send_personal_message(error.model_dump(), websocket)
                    continue
                
                try:
                    message_create = MessageCreate(**message_data)
                except Exception as e:
                    error = ErrorResponse(message=f"Invalid data: {e}")
                    await manager.send_personal_message(error.model_dump(), websocket)
                    continue
                
                message_number = await manager.get_next_message_number(db, connection_id)
                message = await manager.save_message(
                    db, 
                    message_create.text, 
                    connection_id, 
                    message_number
                )
                
                response = MessageResponse(
                    id=message.id,
                    text=message.text,
                    connection_id=str(message.connection_id),
                    user_message_number=message.user_message_number,
                    created_at=message.created_at,
                )
                
                #await manager.send_personal_message(response.model_dump(), websocket) # personal chats
                await manager.broadcast(response.model_dump()) #public chat
                logger.info(f"Message #{message_number} saved for {connection_id}")
                
            except json.JSONDecodeError as e:
                error = ErrorResponse(message=f"Invalid JSON: {e}")
                await manager.send_personal_message(error.model_dump(), websocket)
            except Exception as e:
                logger.error(f"Error processing message from {client_ip}: {e}")
                error = ErrorResponse(message="Internal server error")
                await manager.send_personal_message(error.model_dump(), websocket)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_ip}")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket endpoint: {e}")
        manager.disconnect(websocket)