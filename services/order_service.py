"""
Логика работы с заказами: создание, список, изменение статуса.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Order, OrderStatus


async def create_order(
    session: AsyncSession,
    owner_id: int,
    client_id: int,
    title: str,
    price: float,
    status: OrderStatus,
    order_date: datetime | None = None,
) -> Order:
    order = Order(
        owner_id=owner_id,
        client_id=client_id,
        title=title,
        price=price,
        status=status,
        order_date=order_date or datetime.utcnow(),
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def list_orders(session: AsyncSession, owner_id: int) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.owner_id == owner_id)
        .options(selectinload(Order.client))
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_orders_for_client(
    session: AsyncSession, owner_id: int, client_id: int
) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.owner_id == owner_id, Order.client_id == client_id)
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_order(session: AsyncSession, owner_id: int, order_id: int) -> Order | None:
    stmt = (
        select(Order)
        .where(Order.owner_id == owner_id, Order.id == order_id)
        .options(selectinload(Order.client))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def set_order_status(session: AsyncSession, order: Order, status: OrderStatus) -> None:
    order.status = status
    await session.commit()
