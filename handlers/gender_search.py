import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import Search_Connection, Connection, async_session, User
from filters.Captcha_filter import CaptchaFilter
from keyboard.inline.gender_search_kb import gender_search
from keyboard.reply.in_connect_kb import reply_in_connect
from keyboard.reply.register_kb import create_kb_reg_reply
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


@router.message(F.text.in_({'👀 Поиск по полу', 'Поиск по полу',
                            'поиск по полу'}), CaptchaFilter(session_pool=async_session))
async def choose_connect_gender(message: Message,
                         bot: Bot,
                         session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	# Выбрать статус поиска пользователя.
	status_user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = status_user.fetchone()

	if status_user is None:
		# Занести в бд, если как-то не было занесено раннее.
		new_user_search = Search_Connection(user_id=user_id, search_status=1, gender=1, interests=1)
		session.add(new_user_search)
		await session.commit()

	status_user1 = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user1 = status_user1.fetchone()[0]

	# Если режим поиска, то выводить.
	if status_user1 == 2:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb
		)
	# Если есть собеседник
	elif status_user1 == 3:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)
	else:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='Отлично!',
			reply_markup=kb
		)

		await asyncio.sleep(0.1)

		kb = await gender_search()
		await bot.send_message(
			chat_id=message.chat.id,
			text='Выбери, по какому полу будем искать:',
			reply_markup=kb)


@router.callback_query(F.data.startswith('search_gen_'))
async def inline_search_gender(
		callback: CallbackQuery,
		bot: Bot,
		session: AsyncSession) -> None:
	try:
		user_id: int = callback.from_user.id
		data: any = callback.data.split('_')[2]

		status_user = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		status_user = status_user.fetchone()

		if status_user is not None:
			status_user = status_user[0]

		if data == 'muj':
			await bot.delete_message(
				chat_id=callback.message.chat.id,
				message_id=callback.message.message_id
			)

			if status_user == 1:
				# Выставляем нужные значения для поиска.
				await session.execute(
					update(Search_Connection).
					where(Search_Connection.user_id == user_id).
					values(pol_search='muj', search_status=2, gender=2))
				await session.commit()

				kb = await stop_search_kb()
				await bot.send_message(
					chat_id=callback.message.chat.id,
					text='🔎 Идёт поиск собеседника мужского пола...',
					reply_markup=kb
				)

				# Ищет всех users где их статус == 2, в поиске пола, мужской пол и создаёт связь.
				search_user_to_message = await session.execute(select(Search_Connection.user_id).where( Search_Connection.user_id != user_id, Search_Connection.search_status == 2, Search_Connection.gender == 2))
				search_user_to_message = search_user_to_message.fetchone()[0]

				users_with_male_gender = await session.execute(select(User.gender).where(User.user_id == search_user_to_message))
				users_with_male_gender = users_with_male_gender.fetchone()[0]

				users_search_gender = await session.execute(
					select(Search_Connection.pol_search).where(User.user_id == search_user_to_message))
				users_search_gender = users_search_gender.fetchone()[0]

				i_with_male_gender = await session.execute(
					select(User.gender).where(User.user_id == user_id))
				i_with_male_gender = i_with_male_gender.fetchone()[0]

				if i_with_male_gender == 'Мужской':
					if users_search_gender == 'muj':
						if users_with_male_gender == 'Мужской':
							if search_user_to_message:
								# ставим статус пользователей на режим общения.
								await session.execute(update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=3))
								await session.execute(update(Search_Connection).where(Search_Connection.user_id == search_user_to_message).values(search_status=3))
								# Создаём колонки связи между пользователями.

								search_status = Connection(user_id=user_id, connect_user_id=search_user_to_message)
								search_status2 = Connection(user_id=search_user_to_message, connect_user_id=user_id)
								session.add(search_status)
								session.add(search_status2)
								await session.commit()

								text = ("😊 Собеседник найден!!\n"
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

				if i_with_male_gender == 'Женский':
					if users_search_gender == 'jen':
						if users_with_male_gender == 'Мужской':
							if search_user_to_message:
								# ставим статус пользователей на режим общения.
								await session.execute(
									update(Search_Connection).where(Search_Connection.user_id == user_id).values(
										search_status=3))
								await session.execute(update(Search_Connection).where(
									Search_Connection.user_id == search_user_to_message).values(search_status=3))

								# Создаём колонки связи между пользователями.
								search_status = Connection(user_id=user_id, connect_user_id=search_user_to_message)
								search_status2 = Connection(user_id=search_user_to_message, connect_user_id=user_id)
								session.add(search_status)
								session.add(search_status2)
								await session.commit()

								text = ("😊 Собеседник найден!!\n"
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
			asyncio.create_task(cancel_search_after_timeout(user_id, callback, bot, session))

		elif data == 'jen':
			await bot.delete_message(
				chat_id=callback.message.chat.id,
				message_id=callback.message.message_id
			)
			if status_user == 1:
				# выставляем для поиска по женскому полу верные значения.
				await session.execute(
					update(Search_Connection).
					where(Search_Connection.user_id == user_id).
					values(pol_search='jen', search_status=2,gender=2))
				await session.commit()

				kb = await stop_search_kb()
				await bot.send_message(
					chat_id=callback.message.chat.id,
					text='🔎 Идёт поиск собеседника мужского пола...',
					reply_markup=kb
				)

				# Ищет всех users где их статус == 2, в поиске пола, мужской пол и создаёт связь.
				search_user_to_message = await session.execute(select(Search_Connection.user_id).where( Search_Connection.user_id != user_id, Search_Connection.search_status == 2, Search_Connection.gender == 2))
				search_user_to_message = search_user_to_message.fetchone()[0]

				users_with_male_gender = await session.execute(select(User.gender).where(User.user_id == search_user_to_message))
				users_with_male_gender = users_with_male_gender.fetchone()[0]

				users_search_gender = await session.execute(
					select(Search_Connection.pol_search).where(User.user_id == search_user_to_message))
				users_search_gender = users_search_gender.fetchone()[0]

				i_with_male_gender = await session.execute(
					select(User.gender).where(User.user_id == user_id))
				i_with_male_gender = i_with_male_gender.fetchone()[0]

				if i_with_male_gender == 'Женский':
					if users_search_gender == 'jen':
						if users_with_male_gender == 'Женский':
							if search_user_to_message:
								# ставим статус пользователей на режим общения.
								await session.execute(update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=3))
								await session.execute(update(Search_Connection).where(Search_Connection.user_id == search_user_to_message).values(search_status=3))

								# Создаём колонки связи между пользователями.
								search_status = Connection(user_id=user_id, connect_user_id=search_user_to_message)
								search_status2 = Connection(user_id=search_user_to_message, connect_user_id=user_id)
								session.add(search_status)
								session.add(search_status2)
								await session.commit()

								text = ("😊 Собеседник найден!!\n"
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

				if i_with_male_gender == 'Мужской':
					if users_search_gender == 'muj':
						if users_with_male_gender == 'Женский':
							if search_user_to_message:
								# ставим статус пользователей на режим общения
								await session.execute(
									update(Search_Connection).where(Search_Connection.user_id == user_id).values(
										search_status=3))
								await session.execute(update(Search_Connection).where(
									Search_Connection.user_id == search_user_to_message).values(search_status=3))

								# Создаём колонки связи между пользователями
								search_status = Connection(user_id=user_id, connect_user_id=search_user_to_message)
								search_status2 = Connection(user_id=search_user_to_message, connect_user_id=user_id)
								session.add(search_status)
								session.add(search_status2)
								await session.commit()

								text = ("😊 Собеседник найден!!\n"
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
			asyncio.create_task(cancel_search_after_timeout(user_id, callback, bot, session))
	except Exception as e:
		print('Ошибка в секторе handlers/gender_search/inline_search_gender\n'
				f'{e}')


async def cancel_search_after_timeout(user_id, callback, bot, session) -> None:
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
				chat_id=callback.message.chat.id,
				text="Нам не удалось никого найти, попробуйте ещё раз!",
				reply_markup=keyboard
			)

	except Exception as e:
		print('Ошибка в секторе handlers/gender_search/cancel_search_after_timeout\n'
				f'{e}')