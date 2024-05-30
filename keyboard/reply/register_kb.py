from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def create_kb_reg_reply() -> ReplyKeyboardMarkup:
	"""
	ReplyKeyboardMarkup клавиатура
	для пользователя прошедшего
	регистрацию.
	"""
	keyboard = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='🧩 Поиск собеседника')],
					[KeyboardButton(text='👀 Поиск по полу')],
					[KeyboardButton(text='🌟 Интересы поиска')]
				],
				resize_keyboard=True,
			)
	return keyboard