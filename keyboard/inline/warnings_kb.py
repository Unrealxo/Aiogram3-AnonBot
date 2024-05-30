from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def alert_current(current_id) -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text='👍🏻', callback_data=f'alert_like'),
			InlineKeyboardButton(text='👎🏻', callback_data=f'alert_dis')
		],
		[
			InlineKeyboardButton(text='⚠️ Пожаловаться', callback_data=f'alertuser_{current_id}')
		],
			]
	keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
	return keyboard


async def alert_user(user_id) -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text='👍🏻', callback_data=f'alert_like'),
			InlineKeyboardButton(text='👎🏻', callback_data=f'alert_dis')
		],
		[
			InlineKeyboardButton(text='⚠️ Пожаловаться', callback_data=f'alertuser_{user_id}')
		],
		]
	keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
	return keyboard


async def alert_user_kb(user_id) -> InlineKeyboardMarkup:
	buttons = [
	[
		InlineKeyboardButton(text='📋  Реклама', callback_data=f'jal_advertisment_{user_id}')
	],
	[
		InlineKeyboardButton(text='⌛ Насилие', callback_data=f'jal_nasilie_{user_id}')
	],
	[
		InlineKeyboardButton(text='💰  Продажа', callback_data=f'jal_sell_{user_id}')
	],
	[
		InlineKeyboardButton(text='🔞 Порнография', callback_data=f'jal_porn_{user_id}')
	],
	[
		InlineKeyboardButton(text=' ✍🏻 Попрошайничество', callback_data=f'jal_popros_{user_id}')
	],
	[
		InlineKeyboardButton(text='🥱 Оскорбление', callback_data=f'jal_osk_{user_id}')
	],
	[
		InlineKeyboardButton(text='🤔 Пошлый собеседник', callback_data=f'jal_posl_{user_id}')
	],
	[
		InlineKeyboardButton(text='↩️ Назад', callback_data=f'back_jal_{user_id}')
	],

		]
	keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
	return keyboard