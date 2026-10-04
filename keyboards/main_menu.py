"""
Клавиатура главного меню и меню личного кабинета.
"""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

MAIN_MENU_BUTTONS = {
    "clients": "👥 Клиенты",
    "orders": "📦 Заказы",
    "stats": "📊 Статистика",
    "export": "📄 Экспорт отчета",
    "settings": "⚙️ Настройки",
}


def main_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=MAIN_MENU_BUTTONS["clients"]),
         KeyboardButton(text=MAIN_MENU_BUTTONS["orders"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["stats"]),
         KeyboardButton(text=MAIN_MENU_BUTTONS["export"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["settings"])],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def skip_cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➡️ Пропустить")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )
