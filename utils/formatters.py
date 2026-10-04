"""
Функции форматирования текста для сообщений бота.
"""
from models import Client, Order, ORDER_STATUS_LABELS


def format_client_card(client: Client, orders_count: int = 0) -> str:
    lines = [
        f"👤 <b>{client.name}</b>",
        f"📞 Телефон: {client.phone or '—'}",
        f"✉️ Email: {client.email or '—'}",
    ]
    if client.comment:
        lines.append(f"💬 Комментарий: {client.comment}")
    lines.append(f"📦 Заказов: {orders_count}")
    return "\n".join(lines)


def format_order_line(order: Order) -> str:
    status_label = ORDER_STATUS_LABELS[order.status]
    date_str = order.order_date.strftime("%d.%m.%Y")
    return (
        f"#{order.id} · {order.title}\n"
        f"   {status_label} · {order.price:.2f} ₽ · {date_str}"
    )


def format_money(value: float) -> str:
    return f"{value:,.2f} ₽".replace(",", " ")
