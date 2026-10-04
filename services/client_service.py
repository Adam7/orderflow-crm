"""
Логика работы с клиентами: создание, поиск, список.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Client, Order


async def create_client(
    session: AsyncSession,
    owner_id: int,
    name: str,
    phone: str | None,
    email: str | None,
    comment: str | None,
) -> Client:
    client = Client(
        owner_id=owner_id, name=name, phone=phone, email=email, comment=comment
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def search_clients(session: AsyncSession, owner_id: int, query: str) -> list[Client]:
    stmt = (
        select(Client)
        .where(Client.owner_id == owner_id)
        .where(Client.name.ilike(f"%{query}%"))
        .order_by(Client.name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_clients(session: AsyncSession, owner_id: int) -> list[Client]:
    stmt = select(Client).where(Client.owner_id == owner_id).order_by(Client.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_client(session: AsyncSession, owner_id: int, client_id: int) -> Client | None:
    stmt = select(Client).where(Client.owner_id == owner_id, Client.id == client_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def count_orders_for_client(session: AsyncSession, client_id: int) -> int:
    stmt = select(func.count(Order.id)).where(Order.client_id == client_id)
    result = await session.execute(stmt)
    return result.scalar_one()
