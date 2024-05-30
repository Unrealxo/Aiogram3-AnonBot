from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import Search_Connection, Connection, async_session
from filters.Captcha_filter import CaptchaFilter
from keyboard.reply.register_kb import create_kb_reg_reply
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


@router.message(Command('link'), CaptchaFilter(session_pool=async_session))
async def send_link(message: Message, bot: Bot, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids_result = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id)
	)
	current_ids = current_ids_result.fetchone()

	if status_user == 3:
		link_text = 'Вот мой профиль!'
		link = (f"<b>Ссылка на аккаунт пользователя:</b>\n\n"
		        f"<a href='tg://openmessage?user_id={user_id}'>{link_text}</a>")

		await bot.send_message(
			chat_id=current_ids[0],
			text=link
		)
		await bot.send_message(
			chat_id=message.chat.id,
			text='<b>Ссылка успешно отправлена!</b>'
		)

	elif status_user == 2:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb
		)

	elif status_user == 1:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text='<b>Вы ни с кем не в диалоге!</b>',
			reply_markup=keyboard
		)