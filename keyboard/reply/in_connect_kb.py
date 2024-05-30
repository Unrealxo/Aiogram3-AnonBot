from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def reply_in_connect() -> ReplyKeyboardMarkup:
	keyboard = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='⭕ Завершить чат')],
					[KeyboardButton(text='🥱 Следующий собеседник')],
					[KeyboardButton(text='✍🏻 Отправить ссылку на профиль')]
				],
				resize_keyboard=True,
			)
	return keyboard