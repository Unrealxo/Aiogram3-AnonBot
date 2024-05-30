from aiogram.fsm.state import StatesGroup, State


class settings(StatesGroup):
	gender = State()
	age = State()
	name = State()