from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import User


async def search_interests(
        session: AsyncSession,
        user_id
        ) -> InlineKeyboardMarkup:
    result = await session.execute(select(User.user_interests).where(User.user_id == user_id))

    user_interests_str = result.scalar_one_or_none()
    if user_interests_str:
        user_interests = user_interests_str.split(', ')
    else:
        user_interests = []

    predefined_interests = ['Общение', 'Аниме', 'Любовь', 'Фильмы', 'Одиночество', 'Юмор', 'Флирт', 'Питомцы']

    inline = []
    row = []

    for interest in predefined_interests:
        button_text = interest
        callback_data = f"inter_{interest}"

        if interest in user_interests:
            button_text += " ✅"

        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        row.append(button)

        if len(row) == 2:
            inline.append(row)
            row = []

    reset_button = InlineKeyboardButton(text='❌ Сбросить все интересы', callback_data='inter_reset_interests')
    inline.append([reset_button])

    ikb = InlineKeyboardMarkup(inline_keyboard=inline)
    return ikb
