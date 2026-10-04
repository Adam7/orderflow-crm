"""
Клавиатуры для раздела "Заказы".
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from models import Client, Order, OrderStatus, ORDER_STATUS_LABELS


def orders_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="➕ Новый заказ")],
        [KeyboardButton(text="📋 Все заказы")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def choose_client_kb(clients: list[Client]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=c.name, callback_data=f"pick_client:{c.id}")]
        for c in clients
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def choose_status_kb(prefix: str = "pick_status") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"{prefix}:{status.value}")]
        for status, label in ORDER_STATUS_LABELS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def orders_list_kb(orders: list[Order]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"#{o.id} {o.title} · {ORDER_STATUS_LABELS[o.status]}",
            callback_data=f"order_card:{o.id}",
        )]
        for o in orders
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def order_card_kb(order_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="🔄 Изменить статус", callback_data=f"change_status:{order_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def change_status_kb(order_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"set_status:{order_id}:{status.value}")]
        for status, label in ORDER_STATUS_LABELS.items()
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"order_card:{order_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
