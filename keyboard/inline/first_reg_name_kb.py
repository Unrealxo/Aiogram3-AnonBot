from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def first_reg_name_kb() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='Не указывать никнейм', callback_data='dont_nickname'),
	    ]

    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def first_reg_age_kb() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='Не указывать возраст', callback_data='dont_age')
	    ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard