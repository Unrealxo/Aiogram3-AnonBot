import datetime

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from State.state_reg import Register_anketa
from database.database_postgres import User, Search_Connection
from keyboard.inline.first_reg_name_kb import first_reg_name_kb, first_reg_age_kb
from keyboard.inline.register_kb import choose_gender
from keyboard.reply.register_kb import create_kb_reg_reply

router = Router()


@router.callback_query(F.data.startswith('gender_'), Register_anketa.gender)
async def gender_check(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
	# Проверка на пол пользователя.
	gender = callback.data.split('_')[1]

	if gender == 'male':
		await state.update_data(gender='Мужской')

		kb = await first_reg_age_kb()
		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text="🧩 Теперь определимся с возрастом!",
			reply_markup=kb
		)
		await state.set_state(Register_anketa.age)

	elif gender == 'female':
		await state.update_data(gender='Женский')

		kb = await first_reg_age_kb()
		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text="🧩 Теперь определимся с возрастом!",
			reply_markup=kb
		)
		await state.set_state(Register_anketa.age)

	else:
		gen = await choose_gender()

		await bot.send_message(
			chat_id=callback.message.chat.id,
			text="🤖 Выбери свой пол:",
			reply_markup=gen
		)


@router.message(Register_anketa.gender)
async def gender_error(message: Message, bot: Bot) -> None:
	# Если пользователь отправил сообщение и не выбрал callback запрос.
	gender = await choose_gender()

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
		print('Ошибка в секторе handlers/register_anketa/gender_error'
		      f'{e}, сообщение для удаления не найдено')


@router.message(Register_anketa.age)
async def age_choosen(message: Message, bot: Bot, state: FSMContext) -> None:
	age: any = message.text

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
		kb = await first_reg_name_kb()
		await bot.send_message(
			chat_id=message.chat.id,
			text='🌟 Теперь напиши свой никнейм!',
			reply_markup=kb
		)

		await state.update_data(age=age)
		await state.set_state(Register_anketa.name)


@router.callback_query(F.data == 'dont_age', Register_anketa.age)
async def name_choosen(callback: CallbackQuery, bot: Bot,
                          state: FSMContext) -> None:
	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	await state.update_data(age=None)

	kb = await first_reg_name_kb()
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text='🌟 Теперь напиши свой никнейм!',
		reply_markup=kb
	)
	await state.set_state(Register_anketa.name)


@router.callback_query(F.data == 'dont_age')
async def without_age(callback: CallbackQuery, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User).where(User.user_id == user_id))
	search_row = search.fetchone()
	search = search_row[0] if search_row is not None else None

	if search is not None:
		await callback.answer(
			chat_id=callback.message.chat.id,
			text='Ваш никнейм уже есть в базе данных!',
			show_alert=True
		)


@router.callback_query(F.data == 'dont_nickname', Register_anketa.name)
async def without_nickname(callback: CallbackQuery, bot: Bot,
                          state: FSMContext, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User).where(User.user_id == user_id))
	search_row = search.fetchone()
	search = search_row[0] if search_row is not None else None

	if search is None:
		await bot.delete_message(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id
		)

		data = await state.get_data()
		gender = data.get('gender')
		age = data.get('age')

		user = await session.execute(select(User.user_id).where(User.user_id == user_id))
		search = await session.execute(select(Search_Connection.user_id).where(Search_Connection.user_id == user_id))

		user_result = user.fetchone() if user is not None else None
		search_result = search.fetchone() if search is not None else None

		user = user_result[0] if user_result is not None else None
		search = search_result[0] if search_result is not None else None

		tri_days_later = datetime.datetime.now() + datetime.timedelta(days=30)
		formatted_time = tri_days_later.strftime("%Y:%m:%d %H:%M:%S")

		if user is None:
			user_reg = User(user_id=user_id, gender=gender, age=age, spoiler=1, date_nickname=formatted_time)
			session.add(user_reg)

		if search is None:
			search_reg = Search_Connection(user_id=user_id, search_status=1, interests=1, gender=1)
			session.add(search_reg)
		await session.commit()

		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=callback.message.chat.id,
			text='😊 Регистрация успешно пройдена!',
			reply_markup=keyboard
		)
		await state.clear()


@router.callback_query(F.data == 'dont_nickname')
async def name_choose_fsm(callback: CallbackQuery, bot: Bot,
                          state: FSMContext, session: AsyncSession) -> None:
	user_id: int = callback.from_user.id

	search = await session.execute(select(User).where(User.user_id == user_id))
	search_row = search.fetchone()
	search = search_row[0] if search_row is not None else None

	if search is not None:
		await callback.answer(
			chat_id=callback.message.chat.id,
			text='Ваш никнейм уже есть в базе данных!',
			show_alert=True
		)


@router.message(Register_anketa.name)
async def name_user(message: Message, bot: Bot,
                          state: FSMContext, session: AsyncSession) -> None:
	name: any = message.text

	nick = await session.execute(select(User.nickname).where(User.nickname == name))
	nick = nick.fetchone()

	if nick is not None and nick[0] is not None:
		await bot.send_message(
			chat_id=message.chat.id,
			text='Такой ник уже есть в базе данных!'
		)
		return

	if len(name) <= 2 or len(name) > 20:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Вы должны ввести корректное имя'
		)

	elif len(name.split()) > 1:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Имя не должно содержать пробелов'
		)

	elif not name.isalnum():
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Имя может содержать только буквы и цифры'
		)

	elif not name.isascii():
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Имя может содержать только английские символы'
		)
	else:
		# Вывод всех полученных данных и занос в БД.
		await state.update_data(name=name)
		data = await state.get_data()
		user_id = message.from_user.id
		gender = data.get('gender')
		name = data.get('name')
		age = data.get('age')

		user = await session.execute(select(User.user_id).where(User.user_id == user_id))
		search = await session.execute(select(Search_Connection.user_id).where(Search_Connection.user_id == user_id))

		user_result = user.fetchone() if user is not None else None
		search_result = search.fetchone() if search is not None else None

		user = user_result[0] if user_result is not None else None
		search = search_result[0] if search_result is not None else None

		tri_days_later = datetime.datetime.now() + datetime.timedelta(days=30)
		formatted_time = tri_days_later.strftime("%Y:%m:%d %H:%M:%S")

		if user is None:
			user_reg = User(user_id=user_id, gender=gender, nickname=name, age=age, spoiler=1, date_nickname=formatted_time)
			session.add(user_reg)

		if search is None:
			search_reg = Search_Connection(user_id=user_id, search_status=1, interests=1, gender=1)
			session.add(search_reg)
		await session.commit()

		keyboard = await create_kb_reg_reply()
		await bot.send_message(
			chat_id=message.chat.id,
			text='😊 Регистрация успешно пройдена!',
			reply_markup=keyboard
		)
		await state.clear()