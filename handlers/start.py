from aiogram import Bot
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import async_session, User, Search_Connection
from filters.Captcha_filter import CaptchaFilter
from filters.Chat_Type_filter import ChatTypeFilter
from keyboard.reply.register_kb import create_kb_reg_reply
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


# START OBJECT
@router.message(ChatTypeFilter(chat_type=['private']), CommandStart(),
                CaptchaFilter(session_pool=async_session))
async def command_start(message: Message, bot: Bot,
                        session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/start/command_start'
		      f'{e}, не найден статус пользователя.')

	if user_status == 2:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb
		)
		return

	elif user_status == 3:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)
		return

	# Проверка пользователя на сущестование анкеты.
	user_id_check = await session.execute(select(User.user_id).filter_by(user_id=user_id))
	user_ids = user_id_check.fetchone()

	if user_ids and user_ids[0] == user_id:
		user_status = await session.execute(select(Search_Connection.user_id).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()

		if user_status is None or user_status[0] is None:
			search_status = Search_Connection(user_id=user_id, search_status=1, interests=1, gender=1)
			session.add(search_status)
			await session.commit()

		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
		    text='<b>Добро пожаловать!</b>',
		reply_markup=keyboard
		)

	else:
		user = await session.execute(select(User.user_id).where(User.user_id == user_id))
		search = await session.execute(select(Search_Connection.user_id).where(Search_Connection.user_id == user_id))

		user_result = user.fetchone() if user is not None else None
		search_result = search.fetchone() if search is not None else None

		user = user_result[0] if user_result is not None else None
		search = search_result[0] if search_result is not None else None

		gender = 'Мужской'

		if user is None:
			user_reg = User(user_id=user_id, gender=gender, spoiler=1)
			session.add(user_reg)

		if search is None:
			search_reg = Search_Connection(user_id=user_id, search_status=1, interests=1, gender=1)
			session.add(search_reg)
		await session.commit()

		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text='<b>Добро пожаловать!</b>',
			reply_markup=keyboard
		)