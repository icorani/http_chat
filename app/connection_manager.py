"""
Менеджер WebSocket соединений с поддержкой БД
"""
import logging
from uuid import UUID
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from fastapi import WebSocket
from .models import Message, generate_connection_id
from .schemas import MessageResponse

import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger("connection_manager")

class ConnectionManager:
    """
    Управляет WebSocket соединениями и взаимодействием с базой данных.
    
    Отвечает за:
    - Хранение активных соединений
    - Нумерацию сообщений для каждого connection_id
    - Сохранение и загрузку сообщений из БД
    """
    
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}
        logger.info("ConnectionManager инициализирован")
    
    async def connect(self, websocket: WebSocket) -> UUID:
        """
        Принимает новое WebSocket соединение и генерирует для него connection_id.
        
        Returns:
            UUID: Уникальный идентификатор соединения
        """
        await websocket.accept()
        connection_id = generate_connection_id()
        
        self.active_connections[connection_id] = websocket
        logger.info(f"Новое подключение: {connection_id}. Всего: {len(self.active_connections)}")
        
        return connection_id
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Удаляет соединение из активных.
        """
        # Ищем connection_id по websocket объекту
        connection_id = None
        for cid, ws in self.active_connections.items():
            if ws == websocket:
                connection_id = cid
                break
        
        if connection_id:
            del self.active_connections[connection_id]
            logger.info(f"Отключение: {connection_id}. Осталось: {len(self.active_connections)}")
    
    async def get_next_message_number(self, db: AsyncSession, connection_id: UUID) -> int:
        """
        Получает следующий порядковый номер сообщения для указанного connection_id.
        
        Args:
            db: Сессия базы данных
            connection_id: UUID соединения
            
        Returns:
            int: Следующий номер (начинается с 1)
        """
        try:
            # Ищем максимальный номер для этого connection_id
            result = await db.execute(
                select(func.max(Message.user_message_number))
                .where(Message.connection_id == connection_id)
            )
            max_number = result.scalar()
            
            # Если сообщений еще не было, начинаем с 1
            next_number = 1 if max_number is None else max_number + 1
            logger.debug(f"Следующий номер для {connection_id}: {next_number}")
            
            return next_number
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения номера сообщения для {connection_id}: {e}")
            raise
    
    async def save_message(
        self, 
        db: AsyncSession, 
        text: str, 
        connection_id: UUID, 
        message_number: int
    ) -> Message:
        """
        Сохраняет сообщение в базу данных.
        
        Args:
            db: Сессия базы данных
            text: Текст сообщения
            connection_id: UUID соединения
            message_number: Порядковый номер сообщения
            
        Returns:
            Message: Созданный объект сообщения
        """
        try:
            message = Message(
                text=text,
                connection_id=connection_id,
                user_message_number=message_number
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            logger.debug(f"Сообщение сохранено: {message}")
            return message
            
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Ошибка сохранения сообщения: {e}")
            raise
    
    async def get_message_history(
        self, 
        db: AsyncSession, 
        limit: int = 50
    ) -> List[Message]:
        """
        Получает историю сообщений из базы данных.
        
        Args:
            db: Сессия базы данных
            limit: Максимальное количество сообщений
            
        Returns:
            List[Message]: Список сообщений отсортированных по времени
        """
        try:
            result = await db.execute(
                select(Message)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            messages = result.scalars().all()
            
            # Возвращаем в хронологическом порядке (старые -> новые)
            messages.reverse()
            
            logger.debug(f"Загружено {len(messages)} сообщений из истории")
            return messages
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка загрузки истории: {e}")
            raise
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, cls=DateTimeEncoder))
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
    
    async def broadcast(self, message: dict):
        disconnected = []
        json_message = json.dumps(message, cls=DateTimeEncoder)
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json_message)
            except Exception:
                disconnected.append(connection_id)
        
        for connection_id in disconnected:
            del self.active_connections[connection_id]
    
    def get_connection_count(self) -> int:
        """Возвращает количество активных соединений."""
        return len(self.active_connections)