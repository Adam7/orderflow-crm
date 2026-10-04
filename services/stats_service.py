"""
Логика подсчёта статистики по клиентам и заказам пользователя.
"""
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Client, Order, OrderStatus


@dataclass
class Stats:
    total_clients: int
    total_orders: int
    done: int
    in_progress: int
    new: int
    cancelled: int
    total_amount: float


async def get_stats(session: AsyncSession, owner_id: int) -> Stats:
    total_clients_stmt = select(func.count(Client.id)).where(Client.owner_id == owner_id)
    total_clients = (await session.execute(total_clients_stmt)).scalar_one()

    total_orders_stmt = select(func.count(Order.id)).where(Order.owner_id == owner_id)
    total_orders = (await session.execute(total_orders_stmt)).scalar_one()

    def count_by_status(status: OrderStatus) -> int:
        return status  # placeholder, replaced below

    async def _count(status: OrderStatus) -> int:
        stmt = select(func.count(Order.id)).where(
            Order.owner_id == owner_id, Order.status == status
        )
        return (await session.execute(stmt)).scalar_one()

    done = await _count(OrderStatus.DONE)
    in_progress = await _count(OrderStatus.IN_PROGRESS)
    new = await _count(OrderStatus.NEW)
    cancelled = await _count(OrderStatus.CANCELLED)

    amount_stmt = select(func.coalesce(func.sum(Order.price), 0)).where(
        Order.owner_id == owner_id, Order.status != OrderStatus.CANCELLED
    )
    total_amount = float((await session.execute(amount_stmt)).scalar_one())

    return Stats(
        total_clients=total_clients,
        total_orders=total_orders,
        done=done,
        in_progress=in_progress,
        new=new,
        cancelled=cancelled,
        total_amount=total_amount,
    )
