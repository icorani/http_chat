"""
Модели SQLAlchemy для базы данных чата
"""
import logging
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .database import Base

logger = logging.getLogger("models")

class Message(Base):
    """
    Модель сообщения в чате.
    
    Атрибуты:
        id: Уникальный идентификатор сообщения (автоинкремент)
        text: Текст сообщения
        connection_id: UUID идентификатор WebSocket подключения
        user_message_number: Порядковый номер сообщения для ЭТОГО connection_id
        created_at: Время создания сообщения
    
    Индексы:
        idx_connection_id: Для быстрого поиска сообщений по connection_id
        idx_connection_number: Уникальная комбинация connection_id + user_message_number
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    connection_id = Column(
        UUID(as_uuid=True),  # Нативный тип UUID PostgreSQL
        nullable=False,
        index=True
    )
    user_message_number = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Составной уникальный индекс
    __table_args__ = (
        Index(
            'idx_connection_number', 
            'connection_id', 
            'user_message_number', 
            unique=True
        ),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, connection={self.connection_id}, number={self.user_message_number})>"

# Функция для генерации connection_id
def generate_connection_id() -> uuid.UUID:
    """
    Генерирует уникальный идентификатор для WebSocket подключения.
    Возвращает объект UUID.
    """
    return uuid.uuid4()

# Инициализация моделей
logger.debug("Модели SQLAlchemy загружены")