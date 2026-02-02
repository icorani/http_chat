"""
Настройка подключения к базе данных PostgreSQL
"""
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Настраиваем логирование
logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

# Получаем настройки из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5433/websocket_chat"
)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Настраиваем уровень логирования SQLAlchemy
if DEBUG:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)
else:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,  # Логирование SQL запросов только в DEBUG режиме
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для получения сессии БД
async def get_db():
    """
    Dependency для FastAPI endpoints.
    Использование: async with get_db() as session:
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    Инициализация базы данных - создание всех таблиц.
    Вызывается при старте приложения.
    """
    try:
        async with engine.begin() as conn:
            # Создаем все таблицы, определенные в моделях
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False