from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def stop_search_kb() -> ReplyKeyboardMarkup:
	"""
	ReplyKeyboardMarkup клавиатура
	остановки поиска.
	"""
	keyboard = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='🔴 Остановить поиск')]
				],
				resize_keyboard=True,
			)
	return keyboard