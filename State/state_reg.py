from aiogram.fsm.state import StatesGroup, State


class Register_anketa(StatesGroup):
    gender = State()
    name = State()
    age = State()