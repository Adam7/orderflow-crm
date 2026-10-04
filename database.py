"""
Инициализация подключения к базе данных SQLite через SQLAlchemy (async).
"""
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import config
from models import Base

engine = create_async_engine(config.database_url, echo=False)

async_session_maker = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db() -> None:
    """Создаёт таблицы в базе данных, если их ещё нет."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session():
    """Асинхронный контекстный менеджер для получения сессии SQLAlchemy."""
    async with async_session_maker() as session:
        yield session
