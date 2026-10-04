"""
Клавиатуры для раздела "Клиенты".
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from models import Client


def clients_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="➕ Добавить клиента")],
        [KeyboardButton(text="🔎 Найти клиента")],
        [KeyboardButton(text="📋 Список клиентов")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def clients_list_kb(clients: list[Client], prefix: str = "client_card") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=c.name, callback_data=f"{prefix}:{c.id}")]
        for c in clients
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def client_card_kb(client_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="📦 Заказы клиента", callback_data=f"client_orders:{client_id}")],
        [InlineKeyboardButton(text="➕ Новый заказ", callback_data=f"new_order_for:{client_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
