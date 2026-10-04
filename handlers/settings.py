"""
Обработчики раздела "Настройки".
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database import get_session
from keyboards.main_menu import cancel_kb, main_menu_kb
from services.user_service import get_or_create_user, update_business_name
from utils.states import SettingsStates

router = Router(name="settings")


def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить название бизнеса", callback_data="edit_business_name")]
        ]
    )


@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message) -> None:
    async with get_session() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"Текущее название бизнеса: {user.business_name or 'не задано'}"
    )
    await message.answer(text, reply_markup=settings_kb())


@router.callback_query(F.data == "edit_business_name")
async def edit_business_name_start(callback, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_for_business_name)
    await callback.message.answer("Введите новое название бизнеса:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(SettingsStates.waiting_for_business_name)
async def edit_business_name_save(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with get_session() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
        await update_business_name(session, user, message.text.strip())

    await message.answer(
        f"✅ Название бизнеса обновлено: {message.text.strip()}",
        reply_markup=main_menu_kb(),
    )
