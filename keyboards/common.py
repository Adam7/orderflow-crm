"""
Общие клавиатуры, используемые в разных разделах.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_to_main_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🏠 В главное меню", callback_data="go_main_menu")]]
    )
