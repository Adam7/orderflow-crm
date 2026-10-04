"""
Модуль конфигурации проекта.
Загружает переменные окружения из файла .env и предоставляет
единую точку доступа к настройкам приложения.
"""
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env, расположенного рядом с проектом
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_path: str
    database_url: str


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN не найден. Скопируйте .env.example в .env "
            "и укажите токен, полученный у @BotFather."
        )

    db_path = os.getenv("DATABASE_PATH", "database.db")
    db_url = f"sqlite+aiosqlite:///{db_path}"

    return Config(bot_token=token, database_path=db_path, database_url=db_url)


config = load_config()
