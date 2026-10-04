"""
Точка входа в приложение OrderFlow CRM.

Запуск:
    python bot.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import init_db
from handlers import clients, orders, settings, start, statistics


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    await init_db()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Порядок регистрации роутеров важен: более специфичные —
    # обычно связанные с активным состоянием FSM — matched first
    # благодаря фильтрам состояний внутри каждого хендлера.
    dp.include_router(start.router)
    dp.include_router(clients.router)
    dp.include_router(orders.router)
    dp.include_router(statistics.router)
    dp.include_router(settings.router)

    logging.info("OrderFlow CRM запущен и готов принимать сообщения.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен.")
