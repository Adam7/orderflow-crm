"""
Состояния конечных автоматов (FSM) для многошаговых диалогов.
"""
from aiogram.fsm.state import State, StatesGroup


class AddClientStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_comment = State()


class SearchClientStates(StatesGroup):
    waiting_for_query = State()


class CreateOrderStates(StatesGroup):
    choosing_client = State()
    waiting_for_title = State()
    waiting_for_price = State()
    choosing_status = State()
    waiting_for_date = State()


class SettingsStates(StatesGroup):
    waiting_for_business_name = State()
