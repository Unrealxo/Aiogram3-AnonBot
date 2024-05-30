import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from State.settings_state import settings
from database.database_postgres import User, Search_Connection, async_session
from filters.Captcha_filter import CaptchaFilter
from keyboard.inline.register_kb import choose_gender_set, back_kb, back_kb_nick, back_kb_age
from keyboard.inline.settings_kb import settings_kb_user, hide_settings_red, hide_settings_green
from keyboard.reply.search_stop_kb import stop_search_kb

router = Router()


@router.callback_query(F.data.startswith('back_to_settings'),
                       CaptchaFilter(session_pool=async_session))
async def back_button(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
	await state.clear()

	setting_kb = await settings_kb_user()
	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
		reply_markup=setting_kb
	)


@router.message(Command('settings'), CaptchaFilter(session_pool=async_session))
async def settings_py(message: Message, bot: Bot, session: AsyncSession):
	user_id: int = message.from_user.id

	try:
		user_status = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/settings/settings_py'
		      f'{e}, не найден статус пользователя.')

	if user_status == 2:
		kb = await stop_search_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Вы в режиме поиска!\n\n'
			     '<code>Остановите поиск - /cancel</code>',
			reply_markup=kb
		)

	elif user_status == 3:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ У вас уже есть активный собеседник!\n\n'
			     '<code>/next - Следующий собеседник\n'
			     '/stop - Остановить текущий диалог</code>'
		)

	else:
		settings_kb = await settings_kb_user()
		await bot.send_message(
			chat_id=message.chat.id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=settings_kb
		)


@router.callback_query(F.data.startswith('settings_'),
                       CaptchaFilter(session_pool=async_session))
async def call_settings_user(callback: CallbackQuery, bot: Bot,
                             state: FSMContext, session: AsyncSession) -> None:
	data = callback.data.split('_')[1]
	user_id: int = callback.from_user.id

	try:
		user_status = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/settings/call_settings_user'
		      f'{e}, не найден статус пользователя.')

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

	if data == 'name':
		nick_data = await session.execute(select(User.date_nickname).where(User.user_id == user_id))
		nick_data = nick_data.fetchone()

		if nick_data is not None and nick_data[0] is not None:
			nick_date = datetime.datetime.strptime(nick_data[0], "%Y:%m:%d %H:%M:%S")
		else:
			nick_date = None

		current_time = datetime.datetime.now()

		if nick_date is None or current_time >= nick_date:
			nick = await session.execute(select(User.nickname).where(User.user_id == user_id))
			nick = nick.fetchone()

			if nick is not None and nick[0] is not None:
				kb_back = await back_kb_nick()
				await bot.edit_message_text(
					chat_id=callback.message.chat.id,
					message_id=callback.message.message_id,
					text="<i>Имя можно поменять раз в 30 дней!</i>\n\n"
					     "📌 Введите желаемое имя:",
					reply_markup=kb_back
				)
				await state.set_state(settings.name)

			else:
				kb_back = await back_kb()
				await bot.edit_message_text(
					chat_id=callback.message.chat.id,
					message_id=callback.message.message_id,
					text="<i>Имя можно поменять раз в 30 дней!</i>\n\n"
					     "📌 Введите желаемое имя:",
					reply_markup=kb_back
				)
				await state.set_state(settings.name)
		else:
			remaining_days = (nick_date - current_time).days

			kb_back = await back_kb()
			await bot.edit_message_text(
				chat_id=callback.message.chat.id,
				message_id=callback.message.message_id,
				text=f"<i>Вы недавно меняли имя!\n"
				     f"Сменить можно будет только через:\n"
				     f"{remaining_days} дней</i>",
				reply_markup=kb_back
			)

	elif data == 'gender':
		gender = await session.execute(select(User.gender).where(User.user_id == user_id))
		gender = gender.fetchone()
		gender = gender[0] if gender is not None else None

		gender_choose = await choose_gender_set()
		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text=f"Твой пол на данный момент <b>{gender}</b>\n"
			     "🌀 Введите свой пол:",
			reply_markup=gender_choose
		)
		await state.set_state(settings.gender)

	elif data == "age":
		age = await session.execute(select(User.age).where(User.user_id == user_id))
		age = age.fetchone()

		if age is not None and age[0] is not None:
			kb_back = await back_kb_age()
			await bot.edit_message_text(
				chat_id=callback.message.chat.id,
				message_id=callback.message.message_id,
				text="✍🏻 Введите ваш возраст:",
				reply_markup=kb_back
			)
			await state.set_state(settings.age)

		else:
			kb_back = await back_kb()
			await bot.edit_message_text(
				chat_id=callback.message.chat.id,
				message_id=callback.message.message_id,
				text="✍🏻 Введите ваш возраст:",
				reply_markup=kb_back
			)
			await state.set_state(settings.age)

	elif data == "hide":
		randomize_kb = await session.execute(select(User.spoiler).where(User.user_id == user_id))
		randomize_kb = randomize_kb.fetchone()[0]
		text_spoiler = "🟢 Включена."

		kb = await hide_settings_red()

		if randomize_kb == 2:
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


@router.callback_query(F.data.startswith('gen_'), settings.gender)
async def call_froms_gender(callback: CallbackQuery, bot: Bot,
                            session: AsyncSession, state: FSMContext) -> None:
	user_id: int = callback.from_user.id

	try:
		user_status = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		user_status = user_status.fetchone()[0]
	except Exception as e:
		print('Ошибка в секторе handlers/settings/call_froms_gender'
		      f'{e}, не найден статус пользователя.')

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

	gender = callback.data.split('_')[1]
	setting_kb = await settings_kb_user()

	if gender == 'male':
		gender = 'Мужской'

		await session.execute(update(User).where(User.user_id == user_id).values(gender=gender))
		await session.commit()

		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=setting_kb
		)
		await state.clear()

	elif gender == 'female':
		gender = 'Женский'

		await session.execute(update(User).where(User.user_id == user_id).values(gender=gender))
		await session.commit()

		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=setting_kb
		)
		await state.clear()

	else:
		gen = await choose_gender_set()
		await bot.send_message(
			chat_id=callback.message.chat.id,
			text="🤖 Выбери свой пол:",
			reply_markup=gen
		)


@router.message(settings.gender)
async def call_froms_gender_Message_error(message: Message, bot: Bot) -> None:
	# Если пользователь отправил сообщение а не выбрал callback запрос.
	gender = await choose_gender_set()
	await bot.send_message(
		chat_id=message.chat.id,
		text="🤖 Выбери свой пол:",
		reply_markup=gender
	)

	try:
		await bot.delete_message(
			chat_id=message.chat.id,
			message_id=message.message_id - 1
		)
		await bot.delete_message(
			chat_id=message.chat.id,
			message_id=message.message_id
		)
	except Exception as e:
		print('Ошибка в секторе handlers/settings/call_froms_gender_Message_error'
		      f'{e}, не удалилось сообщение.')


@router.message(settings.age)
async def age_choose_fsm(message: Message, bot: Bot,
                         session: AsyncSession, state: FSMContext) -> None:
	age: any = message.text
	user_id: int = message.from_user.id

	if not age.isdigit():
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Введите корректное число'
		)

	elif int(age) < 16 or int(age) > 90:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Введите корректное число'
		)

	else:
		await session.execute(update(User).where(User.user_id == user_id).values(age=age))
		await session.commit()

		setting_kb = await settings_kb_user()
		await bot.send_message(
			chat_id=message.chat.id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=setting_kb
		)
		await state.clear()


@router.callback_query(F.data == 'dont_age_away', settings.age)
async def name_choose_fsm(callback: CallbackQuery, bot: Bot,
                          state: FSMContext, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User).where(User.user_id == user_id))
	search_row = search.fetchone()

	if search_row is not None and search_row[0] is not None:
		await bot.delete_message(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id
		)

		await session.execute(update(User).where(User.user_id  == user_id).values(age=None))
		await session.commit()

		kb = await settings_kb_user()
		await bot.send_message(
			chat_id=callback.message.chat.id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=kb
		)
		await state.clear()


@router.callback_query(F.data == 'dont_age_away')
async def name_choose_fsm(callback: CallbackQuery, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User.age).where(User.user_id == user_id))
	search_row = search.fetchone()

	if search_row is not None and search_row[0] is not None:
		await callback.answer(
			chat_id=callback.message.chat.id,
			text='Ваш возраст уже есть в базе данных!',
			show_alert=True
		)


@router.callback_query(F.data == 'dont_nick_away', settings.name)
async def name_choose_fsm(callback: CallbackQuery, bot: Bot,
                          state: FSMContext, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User).where(User.user_id == user_id))
	search_row = search.fetchone()

	if search_row is not None and search_row[0] is not None:
		await bot.delete_message(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id
		)

		tri_days_later = datetime.datetime.now() + datetime.timedelta(days=30)
		formatted_time = tri_days_later.strftime("%Y:%m:%d %H:%M:%S")

		await session.execute(update(User).where(User.user_id  == user_id).values(nickname=None, date_nickname=formatted_time))
		await session.commit()

		kb = await settings_kb_user()
		await bot.send_message(
			chat_id=callback.message.chat.id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=kb
		)
		await state.clear()


@router.callback_query(F.data == 'dont_nick_away')
async def name_choose_fsm(callback: CallbackQuery, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User.nickname).where(User.user_id == user_id))
	search_row = search.fetchone()

	if search_row is not None and search_row[0] is not None:
		await callback.answer(
			chat_id=callback.message.chat.id,
			text='Ваш никнейм уже есть в базе данных!',
			show_alert=True
		)


@router.message(settings.name)
async def name_choose_fsm(message: Message, bot: Bot,
                          state: FSMContext, session: AsyncSession) -> None:
	name: any = message.text
	user_id: int = message.from_user.id

	nick = await session.execute(select(User.nickname).where(User.nickname == name))
	nick = nick.fetchone()

	if nick is not None and nick[0] is not None:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Такой ник уже есть в базе данных!'
		)
		return

	if len(name) <= 2 or len(name) > 20:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Вы должны ввести корректное имя'
		)

	elif len(name.split()) > 1:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Имя не должно содержать пробелов'
		)

	elif not name.isalnum():
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Имя может содержать только буквы и цифры'
		)

	elif not name.isascii():
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Имя может содержать только английские символы'
		)
	else:
		tri_days_later = datetime.datetime.now() + datetime.timedelta(days=30)
		formatted_time = tri_days_later.strftime("%Y:%m:%d %H:%M:%S")

		await session.execute(update(User).where(User.user_id == user_id).values(nickname=name, date_nickname=formatted_time))
		await session.commit()

		setting_kb = await settings_kb_user()
		await bot.send_message(
			chat_id=message.chat.id,
			text="<code>Выберите тот пункт, который вы хотите изменить.</code>",
			reply_markup=setting_kb
		)
		await state.clear()