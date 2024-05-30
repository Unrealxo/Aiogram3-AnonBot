from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import User, Search_Connection
from filters.IsAdmin_filter import IsAdminFilter
from keyboard.inline.admin_panel_kb import isadmin, isadmin_users, isadmin_unblock
from link_ever import link_message

router = Router()

@router.message(Command('admin'), IsAdminFilter())
async def admin_panel(message: Message, bot: Bot) -> None:
	nickname: str = message.from_user.full_name
	user_id: int = message.from_user.id

	await bot.send_message(
		chat_id=message.chat.id,
		text='🔎...',
		reply_markup=ReplyKeyboardRemove()
	)

	link = await link_message(user_id=user_id, nickname=nickname)
	kb = await isadmin()

	await bot.send_message(
		chat_id=message.chat.id,
		text=f'🔮 Добрый день! {link}\n\n'
		     f'<i>Вас приветствует пункт управления бота.'
		     f' Будьте осторожны с командами'
		     f' - некоторые могут полностью нарушить работу бота</i> 🕹️',
		reply_markup=kb
	)


@router.callback_query(F.data == 'back_menu')
async def back_to_menu(callback: CallbackQuery, bot: Bot) -> None:
	nickname: str = callback.from_user.full_name
	user_id: int = callback.from_user.id
	link = await link_message(user_id=user_id, nickname=nickname)

	kb = await isadmin()

	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		text=f'🔮 Добрый день! {link}\n\n'
		     f'<i>Вас приветствует пункт управления бота.'
		     f' Будьте осторожны с командами'
		     f' - некоторые могут полностью нарушить работу бота</i> 🕹️',
		message_id=callback.message.message_id,
		reply_markup=kb
	)


@router.callback_query(F.data == 'bots_users')
async def users_count(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	count_users = await session.execute(select(func.count()).select_from(User))
	count_users = count_users.scalar()

	count_connections = await session.execute(select(func.count()).where(and_(Search_Connection.search_status == 3)))
	count_connections = count_connections.scalar()

	premium_users = await session.execute(select(func.count()).where(and_(User.is_premium == 2)))
	premium_users = premium_users.scalar()
	if premium_users is None and premium_users[0] is None:
		premium_users = 0

	blocked_users = await session.execute(select(func.count()).where(and_(User.blocked == 1)))
	blocked_users = blocked_users.scalar()
	if blocked_users is None and blocked_users[0] is None:
		premium_users = 0

	kb = await isadmin_users()

	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='🔸 <i>Статистика бота в данный момент:\n\n'
		     f'<b>▏Всего пользователей: {count_users}</b>\n'
		     f'<b>▏Пользователей онлайн: {count_connections}</b>\n'
		     f'<b>▏Премиум пользователей: {premium_users}\n</b>'
		     f'<b>▏Заблокированных пользователей: {blocked_users}</b></i>',
		reply_markup=kb
	)


@router.callback_query(F.data == 'bots_users_unban')
async def unban_user(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	blocked_users = await session.execute(select(User.user_id).where(User.blocked == 1))
	blocked_users = blocked_users.fetchall()

	if blocked_users is None and blocked_users[0] is None:
		await callback.answer(text='Нет заблокированых пользователей!',
		                      show_alert=True)
	else:
		kb = await isadmin_unblock(session)

		await bot.edit_message_text(
			chat_id=callback.message.chat.id,
			message_id=callback.message.message_id,
			text='🌟 Разблокировать пользователей:',
			reply_markup=kb
		)