"""
Обработчики раздела "Клиенты": добавление, поиск, список, карточка клиента.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import get_session
from keyboards.clients_kb import client_card_kb, clients_list_kb, clients_menu_kb
from keyboards.main_menu import cancel_kb, main_menu_kb, skip_cancel_kb
from services.client_service import (
    count_orders_for_client,
    create_client,
    get_client,
    list_clients,
    search_clients,
)
from services.order_service import list_orders_for_client
from services.user_service import get_or_create_user
from utils.formatters import format_client_card, format_order_line
from utils.states import AddClientStates, SearchClientStates
from utils.validators import is_valid_email, is_valid_phone

router = Router(name="clients")


async def _current_user(message: Message):
    async with get_session() as session:
        return await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )


@router.message(F.text == "👥 Клиенты")
async def clients_menu(message: Message) -> None:
    await message.answer("👥 Раздел «Клиенты»", reply_markup=clients_menu_kb())


# ---------- Добавление клиента ----------

@router.message(F.text == "➕ Добавить клиента")
async def add_client_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AddClientStates.waiting_for_name)
    await message.answer("Введите имя клиента:", reply_markup=cancel_kb())


@router.message(F.text == "❌ Отмена")
async def cancel_any_state(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu_kb())


@router.message(AddClientStates.waiting_for_name)
async def add_client_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddClientStates.waiting_for_phone)
    await message.answer("Телефон клиента:", reply_markup=skip_cancel_kb())


@router.message(AddClientStates.waiting_for_phone)
async def add_client_phone(message: Message, state: FSMContext) -> None:
    phone = None
    if message.text != "➡️ Пропустить":
        if not is_valid_phone(message.text):
            await message.answer("⚠️ Похоже, номер телефона некорректен. Введите ещё раз или пропустите:")
            return
        phone = message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(AddClientStates.waiting_for_email)
    await message.answer("Email клиента:", reply_markup=skip_cancel_kb())


@router.message(AddClientStates.waiting_for_email)
async def add_client_email(message: Message, state: FSMContext) -> None:
    email = None
    if message.text != "➡️ Пропустить":
        if not is_valid_email(message.text):
            await message.answer("⚠️ Похоже, email некорректен. Введите ещё раз или пропустите:")
            return
        email = message.text.strip()
    await state.update_data(email=email)
    await state.set_state(AddClientStates.waiting_for_comment)
    await message.answer("Комментарий (необязательно):", reply_markup=skip_cancel_kb())


@router.message(AddClientStates.waiting_for_comment)
async def add_client_comment(message: Message, state: FSMContext) -> None:
    comment = None if message.text == "➡️ Пропустить" else message.text.strip()
    data = await state.get_data()
    await state.clear()

    user = await _current_user(message)
    async with get_session() as session:
        client = await create_client(
            session,
            owner_id=user.id,
            name=data["name"],
            phone=data.get("phone"),
            email=data.get("email"),
            comment=comment,
        )

    await message.answer(
        f"✅ Клиент добавлен:\n\n{format_client_card(client)}",
        reply_markup=clients_menu_kb(),
    )


# ---------- Поиск клиента ----------

@router.message(F.text == "🔎 Найти клиента")
async def search_client_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchClientStates.waiting_for_query)
    await message.answer("Введите имя клиента для поиска:", reply_markup=cancel_kb())


@router.message(SearchClientStates.waiting_for_query)
async def search_client_query(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await _current_user(message)
    async with get_session() as session:
        clients = await search_clients(session, user.id, message.text.strip())

    if not clients:
        await message.answer("😕 Ничего не найдено.", reply_markup=clients_menu_kb())
        return

    await message.answer(
        f"Найдено клиентов: {len(clients)}",
        reply_markup=clients_list_kb(clients),
    )


# ---------- Список клиентов ----------

@router.message(F.text == "📋 Список клиентов")
async def clients_list(message: Message) -> None:
    user = await _current_user(message)
    async with get_session() as session:
        clients = await list_clients(session, user.id)

    if not clients:
        await message.answer("Клиентов пока нет.", reply_markup=clients_menu_kb())
        return

    await message.answer(
        f"Всего клиентов: {len(clients)}",
        reply_markup=clients_list_kb(clients),
    )


# ---------- Карточка клиента ----------

@router.callback_query(F.data.startswith("client_card:"))
async def client_card(callback: CallbackQuery) -> None:
    client_id = int(callback.data.split(":")[1])
    user = await _current_user(callback.message)

    async with get_session() as session:
        client = await get_client(session, user.id, client_id)
        if not client:
            await callback.answer("Клиент не найден", show_alert=True)
            return
        orders_count = await count_orders_for_client(session, client_id)

    await callback.message.answer(
        format_client_card(client, orders_count),
        reply_markup=client_card_kb(client_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("client_orders:"))
async def client_orders(callback: CallbackQuery) -> None:
    client_id = int(callback.data.split(":")[1])
    user = await _current_user(callback.message)

    async with get_session() as session:
        orders = await list_orders_for_client(session, user.id, client_id)

    if not orders:
        await callback.message.answer("У этого клиента пока нет заказов.")
    else:
        text = "\n\n".join(format_order_line(o) for o in orders)
        await callback.message.answer(f"📦 Заказы клиента:\n\n{text}")
    await callback.answer()
