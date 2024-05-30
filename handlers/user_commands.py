import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import Search_Connection, Connection, async_session, User
from filters.Captcha_filter import CaptchaFilter
from keyboard.inline.gender_search_kb import gender_search
from keyboard.inline.warnings_kb import alert_user, alert_current
from keyboard.reply.in_connect_kb import reply_in_connect
from keyboard.reply.register_kb import create_kb_reg_reply
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


@router.message(Command("cancel"), CaptchaFilter(session_pool=async_session))
async def cancel_searching_cancel(message: Message, bot: Bot,
                                  session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/user_commands/cancel_searching_cancel'
		      f'{e}, не найден статус пользователя.')

	if user_status == 1:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы ещё никого не ищете!",
			reply_markup=keyboard
		)

	elif user_status == 2:
		# Останаливаем поиск и ставим нужные нам параметры.
		await session.execute(update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1, gender=1, interests=1))
		await session.commit()

		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы успешно отменили подбор собеседника!",
			reply_markup=keyboard
		)

	elif user_status == 3:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)
	else:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы не в режиме поиска!",
			reply_markup=keyboard
		)


@router.message(F.text == '🔴 Остановить поиск',
                CaptchaFilter(session_pool=async_session))
async def cancel_searching(message: Message, bot: Bot, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/user_commands/cancel_searching'
		      f'{e}, не найден статус пользователя.')

	if user_status == 1:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы ещё никого не ищете!",
			reply_markup=keyboard
		)

	elif user_status == 2:
		# Останаливаем поиск и ставим нужные нам параметры.
		await session.execute(
			update(Search_Connection).where(Search_Connection.user_id == user_id)
			.values(search_status=1, gender=1, interests=1))
		await session.commit()

		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы успешно отменили подбор собеседника!",
			reply_markup=keyboard
		)
	elif user_status == 3:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)
	else:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы не в режиме поиска!",
			reply_markup=keyboard
		)


@router.message(Command('stop'), CaptchaFilter(session_pool=async_session))
async def stop_for_seatching_and_chating(message: Message, bot: Bot,
                                         session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]

		gender = await session.execute(
			select(Search_Connection.gender).where(Search_Connection.user_id == user_id))
		gender = gender.fetchone()[0]

		interes = await session.execute(
			select(Search_Connection.interests).where(Search_Connection.user_id == user_id))
		interes = interes.fetchone()[0]

	except Exception as e:
		print('Ошибка в секторе handlers/user_commands/stop_for_seatching_and_chating'
		      f'{e}')

	if user_status == 1:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы ещё никого не ищете!",
			reply_markup=keyboard
		)

	elif user_status == 2:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb
		)

	elif user_status == 3 and gender == 1 and interes == 1:
		try:
			# Ищем USER_ID нашего собеседника.
			opponetn_to_connecting = await session.execute(
				select(Connection.connect_user_id).where(Connection.user_id == user_id))
			opponetn_to_connecting = opponetn_to_connecting.fetchone()[0]
			# Обновляем наш статус.
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1))
			# Обновляем статус собеседника.
			await session.execute(update(Search_Connection).where(Search_Connection.user_id == opponetn_to_connecting).values(search_status=2))
			opponetn_to_connecting2 = await session.execute(
				select(Search_Connection.search_status).where(Connection.user_id == opponetn_to_connecting))
			opponetn_to_connecting2 = opponetn_to_connecting2.fetchone()[0]
			# Убиарем колонки соединений из бд для рассинхронизации пользователей.

			await session.execute(delete(Connection).where(Connection.user_id == user_id))
			await session.execute(delete(Connection).where(Connection.user_id == opponetn_to_connecting))
			await session.commit()
		except Exception as e:
			print('Ошибка в секторе handlers/user_commands/stop_for_seatching_and_chating'
			      f'{e}. Соединение пользователей потеряно.')

		# Отправляется нам.
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы успешно завершили диалог!",
			reply_markup=keyboard
		)

		await bot.send_message(
			chat_id=opponetn_to_connecting,
			text="Пользователь отключился..."
		)

		await user_raiting(user_id, current_id=opponetn_to_connecting, bot=bot, message=message)

		# Отправляется собеседнику.
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=opponetn_to_connecting,
			text='🔎 Идёт поиск собеседника...',
			reply_markup=kb
		)
		await asyncio.sleep(25)

		if opponetn_to_connecting2 == 2:
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == opponetn_to_connecting).values(search_status=1))
			await session.commit()

			keyboard = await create_kb_reg_reply()
			await bot.send_message(
				chat_id=opponetn_to_connecting,
				text="Нам не удалось никого найти, попробуйте ещё раз!",
				reply_markup=keyboard
			)
	elif user_status == 3 and gender == 2 and interes == 1:
		try:
			# Ищем USER_ID нашего собеседника.
			opponetn_to_connecting = await session.execute(
				select(Connection.connect_user_id).where(Connection.user_id == user_id))
			opponetn_to_connecting = opponetn_to_connecting.fetchone()[0]
			# Обновляем наш статус.
			await session.execute(update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1, gender=1))
			# Обновляем статус собеседника.
			await session.execute(update(Search_Connection).where(Search_Connection.user_id == opponetn_to_connecting).values(search_status=1, gender=1))

			# Убиарем колонки соединений из бд для рассинхронизации пользователей.
			await session.execute(delete(Connection).where(Connection.user_id == user_id))
			await session.execute(delete(Connection).where(Connection.user_id == opponetn_to_connecting))
			await session.commit()
		except Exception as e:
			print('Ошибка в секторе handlers/user_commands/stop_for_seatching_and_chating'
			      f'{e}. Ошибка подключения')

		# Отправляется нам
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы успешно завершили диалог!",
			reply_markup=keyboard
		)

		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=opponetn_to_connecting,
			text="Пользователь отключился...",
			reply_markup=kb
		)

		await user_raiting(user_id, current_id=opponetn_to_connecting, bot=bot, message=message)

		# Отправляется собеседнику.
		kb = await gender_search()
		await bot.send_message(
			chat_id=opponetn_to_connecting,
			text='Выберите, по какому полу будет идти поиск.',
			reply_markup=kb
		)
	else:
		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text="Вы не общались с собеседником, чтобы заканчивать диалог!!",
			reply_markup=keyboard
		)


@router.message(Command('next'), CaptchaFilter(session_pool=async_session))
async def stop_for_seatching_and_chating_next(message: Message, bot: Bot,
                                              session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]

		gender = await session.execute(
			select(Search_Connection.gender).where(Search_Connection.user_id == user_id))
		gender = gender.fetchone()[0]

		interes = await session.execute(
			select(Search_Connection.interests).where(Search_Connection.user_id == user_id))
		interes = interes.fetchone()[0]

		if user_status == 1:
			keyboard = await create_kb_reg_reply()
			await bot.send_message(
				chat_id=message.chat.id,
				text="Вы ещё никого не ищете!",
				reply_markup=keyboard
			)

		elif user_status == 2:
			kb = await stop_search_kb()
			await bot.send_message(
				chat_id=message.chat.id,
				text='❌ Вы в режиме поиска!\n\n'
				     '<code>Остановите поиск - /cancel</code>',
				reply_markup=kb
			)

		elif user_status == 3 and gender == 1 and interes == 1:
			# Ищем USER_ID нашего собеседника.
			opponetn_to_connecting = await session.execute(
				select(Connection.connect_user_id).where(Connection.user_id == user_id))
			opponetn_to_connecting = opponetn_to_connecting.fetchone()[0]
			# Обновляем наш статус.
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=2))

			# Обновляем статус собеседника.
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == opponetn_to_connecting).values(
					search_status=2))
			# Убиарем колонки соединений из бд для рассинхронизации пользователей.
			await session.execute(delete(Connection).where(Connection.user_id == user_id))
			await session.execute(delete(Connection).where(Connection.user_id == opponetn_to_connecting))
			await session.commit()

			await user_raiting(user_id, current_id=opponetn_to_connecting, bot=bot, message=message)

			# Отправляется нам.
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=2))
			await session.commit()

			kb = await stop_search_kb()
			await bot.send_message(
				chat_id=message.chat.id,
				text='🔎 Идёт поиск собеседника...',
				reply_markup=kb
			)

			# Отправляется собеседнику.
			await bot.send_message(
				chat_id=opponetn_to_connecting,
				text="Пользователь отключился..."
			)

			kb = await stop_search_kb()
			await bot.send_message(
				chat_id=opponetn_to_connecting,
				text='🔎 Идёт поиск собеседника...',
				reply_markup=kb
			)

			# Ищет всех users гдеу их статус == 2, и создаёт связь.
			search_user_to_message = await session.execute(
				select(Search_Connection.user_id).where(Search_Connection.search_status == 2,
				                                        Search_Connection.user_id != user_id,
				                                        Search_Connection.gender == 1))

			search_user_to_message = search_user_to_message.fetchone()[0] if search_user_to_message else None

			interests_user_to_search = await session.execute(select(User.user_interests)
			                                                 .where(User.user_id == search_user_to_message))
			interests_user_to_search = interests_user_to_search.fetchall() if interests_user_to_search else None

			interests_user = await session.execute(select(User.user_interests)
			                                       .where(User.user_id == user_id))
			interests_user = interests_user.fetchall() if interests_user else None

			if (not interests_user or not interests_user[0][0]) and (
					not interests_user_to_search or not interests_user_to_search[0][0]):
				if search_user_to_message:
					# ставим статус пользователей на режим общения.
					await session.execute(
						update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=3))
					await session.execute(
						update(Search_Connection).where(Search_Connection.user_id == search_user_to_message).values(
							search_status=3))
					# Создаём колонки связи между пользователями.
					search_status = Connection(user_id=user_id, connect_user_id=search_user_to_message)
					search_status2 = Connection(user_id=search_user_to_message, connect_user_id=user_id)
					session.add(search_status)
					session.add(search_status2)
					await session.commit()

					text = ("😊 Собеседник найден!\n\n"
					        "🕹️Нет общих интересов!\n\n"
					        '<blockquote>/next - Следующий собеседник</blockquote>\n'
					        '<blockquote>/stop - Остановить текущий диалог</blockquote>')

					kb = await reply_in_connect()
					await bot.send_message(
						chat_id=int(search_user_to_message),
						text=text,
						reply_markup=kb
					)
					await bot.send_message(
						chat_id=user_id,
						text=text,
						reply_markup=kb
					)
			asyncio.create_task(cancel_search_after_timeout(user_id, message, bot, session))

			interests_user_to_search = interests_user_to_search[0][0] if interests_user_to_search else None
			interests_user_to_search = set(interests_user_to_search.split(', '))

			interests_user = interests_user[0][0] if interests_user else None
			interests_user = set(interests_user.split(', '))

			if interests_user & interests_user_to_search:
				if search_user_to_message is not None:
					# ставим статус пользователей на режим общуения.
					await session.execute(
						update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=3))
					await session.execute(
						update(Search_Connection).where(Search_Connection.user_id == search_user_to_message).values(
							search_status=3))
					# Создаём колонки связи между пользователями.
					search_status = Connection(user_id=user_id, connect_user_id=search_user_to_message)
					search_status2 = Connection(user_id=search_user_to_message, connect_user_id=user_id)
					session.add(search_status)
					session.add(search_status2)
					await session.commit()

					common_interests = interests_user & interests_user_to_search

					text = ("😊 Собеседник найден!\n\n"
					        f"🕹️ Общие интересы: {', '.join(common_interests)}\n\n"
					        '<blockquote>/next - Следующий собеседник</blockquote>\n'
					        '<blockquote>/stop - Остановить текущий диалог</blockquote>')

					kb = await reply_in_connect()
					await bot.send_message(
						chat_id=int(search_user_to_message),
						text=text,
						reply_markup=kb
					)
					await bot.send_message(
						chat_id=user_id,
						text=text,
						reply_markup=kb
					)

			asyncio.create_task(cancel_search_after_timeout(user_id, message, bot, session))

		elif user_status == 3 and gender == 2 and interes == 1:
			# Ищем USER_ID нашего собеседника .
			opponetn_to_connecting = await session.execute(
				select(Connection.connect_user_id).where(Connection.user_id == user_id))
			opponetn_to_connecting = opponetn_to_connecting.fetchone()[0]
			# Обновляем наш статус.
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1,
				                                                                             gender=1))
			# Обновляем статус собеседника.
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == opponetn_to_connecting).values(
					search_status=1, gender=1))
			# Убиарем колонки соединений из бд для рассинхронизации пользователей.
			await session.execute(delete(Connection).where(Connection.user_id == user_id))
			await session.execute(delete(Connection).where(Connection.user_id == opponetn_to_connecting))
			await session.commit()

			# Отправляется нам.
			kb = await gender_search()
			await bot.send_message(
				chat_id=message.chat.id,
				text="Выбери пол пользователя для поиска!",
				reply_markup=kb
			)
			await bot.send_message(
				chat_id=opponetn_to_connecting,
				text="Пользователь отключился..."
			)

			await user_raiting(user_id, current_id=opponetn_to_connecting, bot=bot, message=message)

			# Отправляется собеседнику.
			kb = await gender_search()
			await bot.send_message(
				chat_id=opponetn_to_connecting,
				text='Выберите, по какому полу будет идти поиск.',
				reply_markup=kb
			)
		else:
			keyboard = await create_kb_reg_reply()
			await bot.send_message(
			chat_id=message.chat.id,
			text="Вы не в режиме общения чтобы скипнуть диалог.",
			reply_markup=keyboard
		)
	except Exception as e:
		print('Ошибка в секторе handlers/user_commands/stop_for_seatching_and_chating_next'
		      f'{e}')


async def cancel_search_after_timeout2(user_id, message, bot, session) -> None:
	try:
		# После таймаута отменяем поиск, если пользователь все еще в режиме поиска.
		status_users = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		status_users = status_users.fetchone()[0]

		await asyncio.sleep(25)

		if status_users == 2:
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1))
			await session.commit()

			keyboard = await create_kb_reg_reply()
			await bot.send_message(
				chat_id=message.chat.id,
				text="Нам не удалось никого найти, попробуйте ещё раз!",
				reply_markup=keyboard
			)

	except Exception as e:
		print('Ошибка в секторе handlers/user_commands/stop_for_seatching_and_chating'
		      f'{e}')


@router.message(F.text == '⭕ Завершить чат', CaptchaFilter(session_pool=async_session))
async def chat_stop_rus(message: Message, bot: Bot, session: AsyncSession) -> None:
	await stop_for_seatching_and_chating(message, bot, session)


@router.message(F.text == '🥱 Следующий собеседник', CaptchaFilter(session_pool=async_session))
async def chat_next_rus(message: Message, bot: Bot, session: AsyncSession) -> None:
	await stop_for_seatching_and_chating_next(message, bot, session)


@router.message(F.text == '✍🏻 Отправить ссылку на профиль',
                CaptchaFilter(session_pool=async_session))
async def chat_next_rus(message: Message, bot: Bot, session: AsyncSession) -> None:
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
			text=f'<b>Вы ни с кем не в диалоге!</b>',
			reply_markup=keyboard
		)


async def cancel_search_after_timeout(user_id, message, bot, session) -> None:
	try:
		await asyncio.sleep(25)

		status_users = await asyncio.wait_for(
			session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id)),
			timeout=10
		)
		status_users = status_users.fetchone()[0]

		if status_users == 2:
			await session.execute(
				update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1))
			await session.commit()

			keyboard = await create_kb_reg_reply()
			await bot.send_message(
				chat_id=message.chat.id,
				text="Нам не удалось никого найти, попробуйте ещё раз!",
				reply_markup=keyboard
			)

	except Exception as e:
		print('Ошибка в секторе handlers/user_commands/cancel_search_after_timeout'
		      f'{e}')


async def user_raiting(user_id, current_id, bot, message) -> None:
	kb = await alert_user(user_id)
	await bot.send_message(
		chat_id=current_id,
		text='<i>Помогайте администрации совершенствовать работу бота</i>',
		reply_markup=kb
	)

	kb = await alert_current(current_id)
	await bot.send_message(
		chat_id=message.chat.id,
		text='<i>Помогайте администрации совершенствовать работу бота</i>',
		reply_markup=kb
	)