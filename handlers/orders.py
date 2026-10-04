"""
Обработчики раздела "Заказы": создание, список, карточка заказа,
изменение статуса.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import get_session
from keyboards.main_menu import cancel_kb, main_menu_kb
from keyboards.orders_kb import (
    change_status_kb,
    choose_client_kb,
    choose_status_kb,
    order_card_kb,
    orders_list_kb,
    orders_menu_kb,
)
from models import OrderStatus, ORDER_STATUS_LABELS
from services.client_service import list_clients
from services.order_service import (
    create_order,
    get_order,
    list_orders,
    set_order_status,
)
from services.user_service import get_or_create_user
from utils.formatters import format_order_line
from utils.states import CreateOrderStates
from utils.validators import is_valid_price, parse_price

router = Router(name="orders")


async def _current_user(message: Message):
    async with get_session() as session:
        return await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )


@router.message(F.text == "📦 Заказы")
async def orders_menu(message: Message) -> None:
    await message.answer("📦 Раздел «Заказы»", reply_markup=orders_menu_kb())


# ---------- Создание заказа ----------

@router.message(F.text == "➕ Новый заказ")
async def new_order_start(message: Message, state: FSMContext) -> None:
    user = await _current_user(message)
    async with get_session() as session:
        clients = await list_clients(session, user.id)

    if not clients:
        await message.answer(
            "Сначала добавьте хотя бы одного клиента (раздел «Клиенты»).",
            reply_markup=orders_menu_kb(),
        )
        return

    await state.set_state(CreateOrderStates.choosing_client)
    await message.answer("Выберите клиента:", reply_markup=choose_client_kb(clients))


@router.callback_query(F.data.startswith("new_order_for:"))
async def new_order_for_client(callback: CallbackQuery, state: FSMContext) -> None:
    client_id = int(callback.data.split(":")[1])
    await state.update_data(client_id=client_id)
    await state.set_state(CreateOrderStates.waiting_for_title)
    await callback.message.answer("Название заказа:", reply_markup=cancel_kb())
    await callback.answer()


@router.callback_query(
    CreateOrderStates.choosing_client, F.data.startswith("pick_client:")
)
async def pick_client_for_order(callback: CallbackQuery, state: FSMContext) -> None:
    client_id = int(callback.data.split(":")[1])
    await state.update_data(client_id=client_id)
    await state.set_state(CreateOrderStates.waiting_for_title)
    await callback.message.answer("Название заказа:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(CreateOrderStates.waiting_for_title)
async def order_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(CreateOrderStates.waiting_for_price)
    await message.answer("Стоимость заказа (число, например 1500):")


@router.message(CreateOrderStates.waiting_for_price)
async def order_price(message: Message, state: FSMContext) -> None:
    if not is_valid_price(message.text):
        await message.answer("⚠️ Введите корректную сумму, например 1500 или 1500.50:")
        return
    await state.update_data(price=parse_price(message.text))
    await state.set_state(CreateOrderStates.choosing_status)
    await message.answer("Выберите статус заказа:", reply_markup=choose_status_kb())


@router.callback_query(
    CreateOrderStates.choosing_status, F.data.startswith("pick_status:")
)
async def order_status_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    status_value = callback.data.split(":")[1]
    data = await state.get_data()
    user = await _current_user(callback.message)

    async with get_session() as session:
        order = await create_order(
            session,
            owner_id=user.id,
            client_id=data["client_id"],
            title=data["title"],
            price=data["price"],
            status=OrderStatus(status_value),
        )

    await state.clear()
    await callback.message.answer(
        f"✅ Заказ создан:\n\n{format_order_line(order)}",
        reply_markup=orders_menu_kb(),
    )
    await callback.answer()


# ---------- Список заказов ----------

@router.message(F.text == "📋 Все заказы")
async def all_orders(message: Message) -> None:
    user = await _current_user(message)
    async with get_session() as session:
        orders = await list_orders(session, user.id)

    if not orders:
        await message.answer("Заказов пока нет.", reply_markup=orders_menu_kb())
        return

    await message.answer(f"Всего заказов: {len(orders)}", reply_markup=orders_list_kb(orders))


@router.callback_query(F.data.startswith("order_card:"))
async def order_card(callback: CallbackQuery) -> None:
    order_id = int(callback.data.split(":")[1])
    user = await _current_user(callback.message)

    async with get_session() as session:
        order = await get_order(session, user.id, order_id)

    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    client_name = order.client.name if order.client else "—"
    text = (
        f"📦 Заказ #{order.id}\n"
        f"Клиент: {client_name}\n"
        f"Название: {order.title}\n"
        f"Стоимость: {order.price:.2f} ₽\n"
        f"Статус: {ORDER_STATUS_LABELS[order.status]}\n"
        f"Дата: {order.order_date.strftime('%d.%m.%Y')}"
    )
    await callback.message.answer(text, reply_markup=order_card_kb(order.id))
    await callback.answer()


# ---------- Изменение статуса ----------

@router.callback_query(F.data.startswith("change_status:"))
async def change_status_prompt(callback: CallbackQuery) -> None:
    order_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        "Выберите новый статус:", reply_markup=change_status_kb(order_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_status:"))
async def set_status(callback: CallbackQuery) -> None:
    _, order_id_str, status_value = callback.data.split(":")
    order_id = int(order_id_str)
    user = await _current_user(callback.message)

    async with get_session() as session:
        order = await get_order(session, user.id, order_id)
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        await set_order_status(session, order, OrderStatus(status_value))

    await callback.message.answer(
        f"✅ Статус заказа #{order_id} изменён на {ORDER_STATUS_LABELS[OrderStatus(status_value)]}"
    )
    await callback.answer()
