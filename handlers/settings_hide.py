from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import User
from keyboard.inline.settings_kb import hide_settings_green, hide_settings_red

settings_router = Router()


@settings_router.callback_query(F.data.startswith('hide_option'))
async def hide_option(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id
	call_data = callback.data.split('_')[2]

	if call_data in ['green']:
		# Пользователь выбирает, что нужно включить защиту медиа.
		await session.execute(update(User).where(User.user_id == user_id).values(spoiler=1))
		await session.commit()
		text_spoiler = "🟢 Включена."
		kb = await hide_settings_red()

		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text="<i>Данная флашка активирует скрытие всех фотографий, "
			     "видео, докуметов, GIF, во время активного диалога. "
			     "Медиа-файлы будут показаны после нажатия кнопки 'Показать'</i>\n\n"
			     f"Сейчас: {text_spoiler}",
			reply_markup=kb
		)

	if call_data in ['red']:
		# Отключение прямого показа после отправки.
		await session.execute(update(User).where(User.user_id == user_id).values(spoiler=2))
		await session.commit()
		kb = await hide_settings_green()
		text_spoiler = "🔴 Выключена."

		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text="<i>Данная флашка активирует скрытие всех фотографий, "
			     "видео, докуметов, GIF, во время активного диалога. "
			     "Медиа-файлы будут показаны после нажатия кнопки 'Показать'</i>\n\n"
			     f"Сейчас: {text_spoiler}",
			reply_markup=kb
		)