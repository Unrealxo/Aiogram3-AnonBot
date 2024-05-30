from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def butt_for_show_photo(photo_hash) -> InlineKeyboardMarkup:
	buttons = [
	[
		InlineKeyboardButton(text='Показать фото', callback_data=f'view_one_photo_{photo_hash}')
		],
	[
		InlineKeyboardButton(text='Показать в этом чате', callback_data=f'view_chat_photo_{photo_hash}')
	]
		]

	keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
	return keyboard