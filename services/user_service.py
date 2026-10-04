"""
Логика регистрации и получения профиля пользователя.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, full_name: str, username: str | None
) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, full_name=full_name, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def update_business_name(session: AsyncSession, user: User, name: str) -> None:
    user.business_name = name
    await session.commit()
