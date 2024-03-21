from aiogram.fsm.state import StatesGroup, State


class Reminder(StatesGroup):
    name = State()
    time = State()
    one_time = State()
    result = State()
