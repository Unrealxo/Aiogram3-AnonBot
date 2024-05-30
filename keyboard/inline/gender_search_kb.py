from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def gender_search() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='Мужской', callback_data='search_gen_muj'),
		    InlineKeyboardButton(text='Женский', callback_data='search_gen_jen')
	    ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard