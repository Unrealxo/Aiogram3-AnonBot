import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import Search_Connection, Connection, async_session, User
from filters.Captcha_filter import CaptchaFilter
from keyboard.reply.in_connect_kb import reply_in_connect
from keyboard.reply.register_kb import create_kb_reg_reply
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


@router.message(F.text.in_({'🧩 Поиск собеседника', 'Поиск собеседника', 'поиск собеседника'}),
                CaptchaFilter(session_pool=async_session), )
async def choose_connect(message: Message,
                         bot: Bot,
                         session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		# Выбрать статус поиска пользователя.
		status_user = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		status_user = status_user.fetchone()
		if status_user is not None:
			pass
		else:
			# Занести в бд, если как-то не было занесено раннее.
			search_status = Search_Connection(user_id=user_id, search_status=1, interests=1, gender=1)
			session.add(search_status)
			spoiler = User(user_id=user_id, spoiler=1)
			session.add(spoiler)
			await session.commit()

		# ищем статус пользователя.
		status_user1 = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		status_user1 = status_user1.fetchone()[0]

		# ищем гендер.
		gender = await session.execute(
			select(Search_Connection.gender).where(Search_Connection.user_id == user_id))
		gender = gender.fetchone()[0]

		# ищем интерес.
		interes = await session.execute(
			select(Search_Connection.interests).where(Search_Connection.user_id == user_id))
		interes = interes.fetchone()[0]

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

		elif status_user1 == 1 and gender == 1 and interes == 1:
			# Если пользователь не в поиске, и не в диалоге ставим статус поиска собеседника.
			await session.execute(update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=2))
			await session.commit()

			kb = await stop_search_kb()
			await bot.send_message(
				chat_id=message.chat.id,
				text='🔎 Идёт поиск собеседника...',
				reply_markup=kb
			)

			# Ищет всех users где их статус == 2, и создаёт связь.
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
					# ставим статус пользователей на режим общения.
					await session.execute(
						update(Search_Connection)
						.where(Search_Connection.user_id == user_id)
						.values(search_status=3))

					await session.execute(
						update(Search_Connection)
					    .where(Search_Connection.user_id == search_user_to_message)
						.values(search_status=3))

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

	except Exception as e:
		print('Ошибка в секторе "choose_connection/choose_connect".\n'
		      f'Ошибка: {e}')


async def cancel_search_after_timeout(user_id, message, bot, session) -> None:
	try:
		await asyncio.sleep(10)

		status_users = await asyncio.wait_for(
			session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id)),
			timeout=10)

		status_users = status_users.fetchone()[0]
		if status_users == 2:
			await session.execute(update(Search_Connection).where(Search_Connection.user_id == user_id).values(search_status=1))
			await session.commit()

			keyboard = await create_kb_reg_reply()
			await bot.send_message(
				chat_id=message.chat.id,
				text="Нам не удалось никого найти, попробуйте ещё раз!",
				reply_markup=keyboard
			)

	except Exception as e:
		print('Ошибка в секторе "choose_connection/cancel_search_after_timeout".\n'
		      f'Ошибка: {e}')