from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import UserAlerts
from keyboard.inline.warnings_kb import alert_user_kb, alert_user

router = Router()


@router.callback_query(F.data.startswith('alertuser_'))
async def user_alerting(callback: CallbackQuery, bot: Bot) -> None:
	user_id: int = int(callback.data.split('_')[1])

	kb = await alert_user_kb(user_id)
	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='<i>Выберите категорию жалобы:</i>',
		reply_markup=kb
	)


@router.callback_query(F.data.startswith('back_jal_'))
async def user_alerting_back(callback: CallbackQuery, bot: Bot) -> None:
	user_id: int = int(callback.data.split('_')[2])

	kb = await alert_user(user_id)
	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='<i>Помогайте администрации совершенствовать работу бота</i>',
		reply_markup=kb
	)


@router.callback_query(F.data.startswith('jal_'))
async def user_alerting_jalobs(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	user_id = int(callback.data.split('_')[2])
	target: str = str(callback.data.split('_')[1])

	user = await session.execute(select(UserAlerts.user_id).where(UserAlerts.user_id == user_id))
	users = user.fetchone()

	if users is None or users[0] is None:
		add = UserAlerts(user_id=user_id)
		session.add(add)
		await session.commit()

	if target == 'advertisment':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(ad=UserAlerts.ad + 1))
	if target == 'nasilie':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(nasilie=UserAlerts.nasilie + 1))
	if target == 'sell':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(sell=UserAlerts.sell + 1))
	if target == 'porn':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(porn=UserAlerts.porn + 1))
	if target == 'popros':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(popros=UserAlerts.popros + 1))
	if target == 'osk':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(osk=UserAlerts.osk + 1))
	if target == 'posl':
		await session.execute(
			update(UserAlerts).where(UserAlerts.user_id == user_id).values(poshl=UserAlerts.poshl + 1))
	await session.commit()

	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='Благодарим за отзыв!'
	)


@router.callback_query(F.data == 'alert_like')
async def user_alerting_like(callback: CallbackQuery, bot: Bot) -> None:

	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='Благодарим за отзыв!'
	)


@router.callback_query(F.data == 'alert_dis')
async def user_alerting_dis(callback: CallbackQuery, bot: Bot) -> None:
	await bot.edit_message_text(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		text='Благодарим за отзыв!'
	)