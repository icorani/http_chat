"""
Pydantic схемы для валидации данных WebSocket чата
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import List, Optional

from pydantic import ConfigDict
import json

# ===== Входящие данные (от клиента к серверу) =====

class MessageCreate(BaseModel):
    """Схема для создания нового сообщения"""
    text: str = Field(..., min_length=1, max_length=1000, description="Текст сообщения")



class MessageResponse(BaseModel):
    type: str = "message"
    id: int
    text: str
    connection_id: str
    user_message_number: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class InitResponse(BaseModel):
    """Схема инициализации при подключении"""
    type: str = "init"
    connection_id: str  # UUID как строка
    history: List[MessageResponse]

class ErrorResponse(BaseModel):
    """Схема для ошибок"""
    type: str = "error"
    message: str

# ===== Вспомогательные схемы =====

class HealthResponse(BaseModel):
    """Схема для health check"""
    status: str
    service: str
    database: bool
    connections: int = 0