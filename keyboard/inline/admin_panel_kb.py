from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from database.database_postgres import User


async def isadmin() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='💎 Пользователи', callback_data='bots_users')
	    ],
	    [
		    InlineKeyboardButton(text='🔴 Жалобы', callback_data='alert_jalobs'),
		    InlineKeyboardButton(text='⌛ Рассылка', callback_data='mass_rassilka')
	    ],
	    [
		    InlineKeyboardButton(text='🌔 Добавление администрации', callback_data='add_admins'),
	    ],
	    [
		    InlineKeyboardButton(text='🌀 Управление премиумом', callback_data='premium_information'),
	    ],
	    [
		    InlineKeyboardButton(text='🥋 Экстренные случаи', callback_data='extreme_situation'),
	    ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def isadmin_users() -> InlineKeyboardMarkup:
    buttons = [
	    [
		    InlineKeyboardButton(text='🕹️ Разблокировка пользователей', callback_data='bots_users_unban')
	    ],
	    [
		    InlineKeyboardButton(text='🎾 Написать пользователю', callback_data='bots_users_write')
	    ],
	    [
		    InlineKeyboardButton(text='↩️ Назад', callback_data='back_menu')
	    ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def isadmin_unblock(session, page=1, page_size=6) -> InlineKeyboardMarkup:
    offset = (page - 1) * page_size
    blocked_users = await session.execute(select(User.user_id)
                                          .where(User.blocked == 1)
                                          .offset(offset)
                                          .limit(page_size))
    blocked_users = blocked_users.fetchall()

    if blocked_users:
        inline = []
        row = []
        count = 1
        for block in blocked_users:
            user_id = block[0]
            button = InlineKeyboardButton(text=str(count), callback_data=f"user_call_{user_id}")
            row.append(button)
            if len(row) == 3:
                inline.append(row)
                row = []
            count += 1
        if row:
            inline.append(row)

        if page > 1:
            prev_button = InlineKeyboardButton(text="<< Предыдущие", callback_data=f"prev_{page - 1}")
            inline.append([prev_button])

        if len(blocked_users) == page_size:
            next_button = InlineKeyboardButton(text="Следующие >>>", callback_data=f"next_{page + 1}")
            inline.append([next_button])

        ikb = InlineKeyboardMarkup(inline_keyboard=inline)
        return ikb