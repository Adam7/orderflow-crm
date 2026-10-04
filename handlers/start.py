"""
Обработчики команды /start, регистрации и личного кабинета.
"""
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import get_session
from keyboards.main_menu import main_menu_kb
from services.stats_service import get_stats
from services.user_service import get_or_create_user

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    async with get_session() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )

    text = (
        f"👋 Добро пожаловать, {user.full_name}!\n\n"
        "Это <b>OrderFlow CRM</b> — система управления клиентами "
        "и заказами для малого бизнеса.\n\n"
        "Выберите раздел в меню ниже 👇"
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == "🏠 Главное меню")
async def go_main_menu(message: Message) -> None:
    await message.answer("🏠 Главное меню", reply_markup=main_menu_kb())


@router.message(F.text == "👤 Личный кабинет")
@router.message(F.text == "/profile")
async def personal_cabinet(message: Message) -> None:
    async with get_session() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
        stats = await get_stats(session, user.id)

    business = user.business_name or "не задано"
    text = (
        "👤 <b>Личный кабинет</b>\n\n"
        f"Имя: {user.full_name}\n"
        f"Бизнес: {business}\n"
        f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n\n"
        f"Клиентов: {stats.total_clients}\n"
        f"Заказов: {stats.total_orders}"
    )
    await message.answer(text, reply_markup=main_menu_kb())
