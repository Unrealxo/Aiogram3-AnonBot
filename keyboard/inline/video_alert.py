from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def butt_for_show_video(video_hash) -> InlineKeyboardMarkup:
	buttons = [
	[
		InlineKeyboardButton(text='Показать видео', callback_data=f'view_one_video_{video_hash}')
		],
	[
		InlineKeyboardButton(text='Показать в этом чате', callback_data=f'view_chat_video_{video_hash}')
	]
		]

	keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
	return keyboard