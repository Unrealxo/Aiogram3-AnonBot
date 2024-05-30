from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def settings_kb_user() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='🌿 Пол', callback_data='settings_gender')
	    ],
	    [
		    InlineKeyboardButton(text='🔮 Возраст', callback_data='settings_age'),
	    ],
	    [
		    InlineKeyboardButton(text='🧩 Имя', callback_data='settings_name'),
	    ],
	    [
		    InlineKeyboardButton(text='💥 Скрытие медиа', callback_data='settings_hide'),
	    ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def hide_settings_green() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='🟢 Включить скрытие медиа', callback_data='hide_option_green'),
	    ],
	    [
		    InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_settings'),
	    ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def hide_settings_red() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='🔴 Выключить скрытие медиа', callback_data='hide_option_red'),
	    ],
	    [
		    InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_settings'),
	    ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
