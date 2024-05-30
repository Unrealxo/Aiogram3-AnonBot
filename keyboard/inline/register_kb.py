from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# inlinekeyboard с выбором пола пользователя.
async def choose_gender() -> InlineKeyboardMarkup:
    buttons = [
        [
	        InlineKeyboardButton(text='Мужской', callback_data='gender_male'),
	        InlineKeyboardButton(text='Женский', callback_data='gender_female'),
		]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def choose_gender_set() -> InlineKeyboardMarkup:
    buttons = [
        [
	        InlineKeyboardButton(text='Мужской', callback_data='gen_male'),
	        InlineKeyboardButton(text='Женский', callback_data='gen_female'),
		],
	    [
		    InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_settings'),
	    ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def back_kb() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_settings'),
	    ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def back_kb_nick() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='Не указывать никнейм', callback_data='dont_nick_away'),
	    ],
	    [
		    InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_settings'),
	    ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def back_kb_age() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='Не указывать возраст', callback_data='dont_age_away'),
	    ],
	    [
		    InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_settings'),
	    ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard