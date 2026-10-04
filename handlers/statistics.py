"""
Обработчики раздела "Статистика" и экспорта отчёта в PDF.
"""
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.types import FSInputFile, Message

from database import get_session
from services.order_service import list_orders
from services.stats_service import get_stats
from services.export_service import generate_report_pdf
from services.user_service import get_or_create_user
from utils.formatters import format_money

router = Router(name="statistics")


async def _current_user(message: Message):
    async with get_session() as session:
        return await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message) -> None:
    user = await _current_user(message)
    async with get_session() as session:
        stats = await get_stats(session, user.id)

    text = (
        "📊 <b>Статистика</b>\n\n"
        f"Всего клиентов: {stats.total_clients}\n"
        f"Всего заказов: {stats.total_orders}\n"
        f"Выполнено: {stats.done}\n"
        f"В работе: {stats.in_progress}\n"
        f"Новых: {stats.new}\n"
        f"Отменено: {stats.cancelled}\n\n"
        f"Общая сумма:\n{format_money(stats.total_amount)}"
    )
    await message.answer(text)


@router.message(F.text == "📄 Экспорт отчета")
async def export_report(message: Message) -> None:
    user = await _current_user(message)
    async with get_session() as session:
        stats = await get_stats(session, user.id)
        orders = await list_orders(session, user.id)

    await message.answer("⏳ Формирую PDF-отчёт...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / f"report_{user.telegram_id}.pdf"
        generate_report_pdf(
            output_path=str(output_path),
            business_name=user.business_name or user.full_name,
            stats=stats,
            orders=orders,
        )
        await message.answer_document(
            FSInputFile(output_path, filename="orderflow_report.pdf"),
            caption="📄 Ваш отчёт готов.",
        )
