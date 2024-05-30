from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import Search_Connection, User, async_session
from filters.Captcha_filter import CaptchaFilter
from keyboard.inline.interests_search_kb import search_interests
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


@router.message(F.text.in_({'🌟 Интересы поиска', 'Интересы поиска',
                            'интересы поиска'}), CaptchaFilter(session_pool=async_session))
async def interests_search(message: Message, bot: Bot, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/interests_search/interests_search'
		      f'{e}, Статус пользователя неизвестен.')

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

	kb_for_interests = await search_interests(session=session, user_id=user_id)
	await bot.send_message(
		chat_id=message.chat.id,
		text='<i>На ваших интересах будет основываться поиск</i>\n\n'
		     '<b>Выберите интересующие Вас интересы:</b>',
		reply_markup=kb_for_interests
	)


@router.callback_query(F.data == 'inter_reset_interests')
async def call_istraction2(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	try:
		user_status = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/interests_search/call_istraction2'
		     f'{e}, Статус пользователя неизвестен.')

	if user_status == 2:
		kb = await stop_search_kb()
		await callback.answer(
			chat_id=callback.message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb,
			show_alert=True
		)
		return

	elif user_status == 3:
		await callback.answer(
			chat_id=callback.message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)
		return

	await session.execute(update(User).where(User.user_id == user_id).values(user_interests=None))
	await session.commit()

	kb_for_interests = await search_interests(session=session, user_id=user_id)
	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='<i>На ваших интересах будет основываться поиск</i>\n\n'
		     '<b>Выберите интересующие Вас интересы:</b>',
		reply_markup=kb_for_interests)


@router.callback_query(F.data.startswith('inter_'))
async def call_istraction(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	call_data: any = callback.data.split('_')[1]
	user_id: int = callback.from_user.id

	try:
		user_status = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/interests_search/call_istraction'
		      f'{e}, Статус пользователя неизвестен.')

	if user_status == 2:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=callback.message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb
		)
		return

	elif user_status == 3:
		await bot.send_message(
			chat_id=callback.message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)
		return

	interests_correct = ['Общение', 'Аниме', 'Любовь', 'Фильмы', 'Одиночество', 'Юмор', 'Флирт', 'Питомцы']

	if call_data in interests_correct:
		interests = await session.execute(select(User.user_interests).where(User.user_id == user_id))
		interests = interests.scalar_one_or_none()

		if interests is not None:
			interests = interests.split(', ')
		else:
			interests = []

		if call_data in interests:
			interests.remove(call_data)
		else:
			interests.append(call_data)

		if interests:
			await session.execute(
				update(User).where(User.user_id == user_id).values(user_interests=', '.join(interests)))
		else:
			await session.execute(
				update(User).where(User.user_id == user_id).values(user_interests=None))
		await session.commit()

		kb_for_interests = await search_interests(session=session, user_id=user_id)
		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text='<i>На ваших интересах будет основываться поиск</i>\n\n'
			     '<b>Выберите интересующие Вас интересы:</b>',
			reply_markup=kb_for_interests)