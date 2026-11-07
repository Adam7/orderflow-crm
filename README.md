# OrderFlow CRM

Информационная система управления клиентами и заказами малого бизнеса,
реализованная в виде Telegram-бота.

## Возможности

- Регистрация пользователей и личный кабинет
- CRUD клиентов: добавление, поиск, список, карточка клиента
- CRUD заказов: создание, список, изменение статуса заказа
- Статистика по клиентам, заказам и выручке
- Экспорт отчёта в PDF (с поддержкой кириллицы)
- Настройки профиля (название бизнеса)

## Стек технологий

- Python 3.11+
- aiogram 3 (асинхронный фреймворк для Telegram Bot API)
- SQLAlchemy 2 (async ORM)
- SQLite (aiosqlite)
- python-dotenv
- reportlab (генерация PDF)

## Структура проекта

```
orderflow/
├── bot.py                  # точка входа, регистрация роутеров
├── config.py                # загрузка конфигурации из .env
├── database.py               # инициализация БД, сессии SQLAlchemy
├── models.py                  # ORM-модели: User, Client, Order
├── requirements.txt
├── .env.example
├── resources/
│   └── fonts/                 # шрифты для корректного PDF-экспорта кириллицы
├── handlers/
│   ├── start.py                # /start, регистрация, личный кабинет
│   ├── clients.py               # раздел "Клиенты"
│   ├── orders.py                 # раздел "Заказы"
│   ├── statistics.py              # статистика и экспорт PDF
│   └── settings.py                 # раздел "Настройки"
├── keyboards/
│   ├── main_menu.py             # клавиатура главного меню
│   ├── clients_kb.py             # инлайн-клавиатуры клиентов
│   ├── orders_kb.py               # инлайн-клавиатуры заказов
│   └── common.py
├── services/                       # бизнес-логика (слой сервисов)
│   ├── user_service.py
│   ├── client_service.py
│   ├── order_service.py
│   ├── stats_service.py
│   └── export_service.py
└── utils/
    ├── states.py                    # состояния FSM
    ├── validators.py                 # валидация ввода
    └── formatters.py                  # форматирование сообщtybz
