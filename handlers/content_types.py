import datetime
import hashlib
import os

from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto, InputMediaVideo
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_postgres import Search_Connection, Connection, User, Photo_user, Video_user
from keyboard.inline.photo_alert import butt_for_show_photo
from keyboard.inline.video_alert import butt_for_show_video

router = Router()


@router.edited_message()
async def editing_messages(message: Message, session: AsyncSession) -> None:
	try:
		user_id = message.from_user.id
		status_user = await session.execute(
			select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		status_user = status_user.fetchone()[0]

		current_ids = await session.execute(
			select(Connection.connect_user_id).where(Connection.user_id == user_id)
		)
		current_ids = current_ids.fetchone()[0]

		user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
		user_nickname = user_nickname.fetchone()[0]

		is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
		premium = is_premium.fetchone()

		if premium or premium[0] == 2:
			premium_emodji = '💎'
		else:
			premium_emodji = ''

		nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
		nickname = nickname.fetchone()

		if nickname is not None and nickname[0] is not None:
			message_text = (f'<b>{user_nickname}{premium_emodji}</b>\n'
			                f'{message.text}')
		else:
			message_text = f'{message.text}'

		if nickname is not None and nickname[0] is not None:
			caption_message = (f'<b>{user_nickname}{premium_emodji}</b>\n'
			                   f'{message.caption}')
		else:
			caption_message = f'{message.caption}'

		if status_user == 3:
			if message.text:
				await message.bot.edit_message_text(message_text, current_ids, message.message_id + 1)

			elif message.caption:
				await message.bot.edit_message_caption(
					caption_message,
					current_ids,
					message.message_id + 1,
					caption_entities=message.caption_entities
				)
	except Exception as e:
		print(f'Ошибка в секторе handlers/content_types/editing_messages\n'
		      f'{e}')


@router.message(F.content_type.in_(["text"]))
async def echo_functions_text(message: Message, session: AsyncSession) -> None:
	try:
		user_id: int = message.from_user.id

		user = await session.execute(select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
		status_user = user.fetchone()[0]

		current_ids = await session.execute(select(Connection.connect_user_id).where(Connection.user_id == user_id))
		current_ids = current_ids.fetchone()[0]

		if status_user == 3:
			if message.content_type == "text":
				reply = None
				if message.reply_to_message:
					if message.reply_to_message.from_user.id == message.from_user.id:
						reply = message.reply_to_message.message_id + 1
					else:
						reply = message.reply_to_message.message_id - 1

				user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
				user_nickname = user_nickname.fetchone()[0]

				is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
				premium = is_premium.fetchone()

				if premium[0] == 2:
					premium_emodji = '💎'
				else:
					premium_emodji = ''

				nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
				nickname = nickname.fetchone()

				if nickname is not None and nickname[0] is not None:
					message_text = (f'<b>{user_nickname}{premium_emodji}</b>\n'
					                f'{message.text}')
				else:
					message_text = f'{message.text}'

				await message.bot.send_message(
					current_ids,
					message_text,
					entities=message.entities,
					reply_to_message_id=reply
				)
	except Exception as e:
		print('Ошибка в секторе handlers/content_types/echo_functions\n'
		      f'{e}')

@router.message(F.content_type.in_(["dice"]))
async def echo_functions_dice(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id)
	)
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		if message.content_type == 'dice':
			await message.bot.send_dice(
				current_ids,
				message.entities
			)


@router.message(F.content_type.in_(["audio"]))
async def echo_functions(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
	user_nickname = user_nickname.fetchone()[0]

	is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
	premium = is_premium.fetchone()

	if premium or premium[0] == 2:
		premium_emodji = '💎'
	else:
		premium_emodji = ''

	nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
	nickname = nickname.fetchone()

	if nickname is not None and nickname[0] is not None:
		message_caption = (f'<b>{user_nickname}{premium_emodji}</b>\n'
		                   f'{message.caption}' if message.caption is not None else f'<b>{user_nickname}</b>\n')
	else:
		message_caption = f'{message.caption}' if message.caption else None

	if status_user == 3:
		if message.content_type == "audio":
			await message.bot.send_audio(
				current_ids,
				message.audio.file_id,
				caption=message_caption
			)


@router.message(F.content_type.in_(["voice"]))
async def echo_functions_voice(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
	user_nickname = user_nickname.fetchone()[0]

	is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
	premium = is_premium.fetchone()

	if premium or premium[0] == 2:
		premium_emodji = '💎'
	else:
		premium_emodji = ''

	nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
	nickname = nickname.fetchone()

	if nickname is not None and nickname[0] is not None:
		message_caption = (f'<b>{user_nickname}{premium_emodji}</b>\n'
		                   f'{message.caption}' if message.caption is not None else f'<b>{user_nickname}</b>\n')
	else:
		message_caption = f'{message.caption}' if message.caption else None

	if status_user == 3:
		if message.content_type == "voice":
			await message.bot.send_voice(
				current_ids,
				message.voice.file_id,
				caption=message_caption
			)


@router.message(F.content_type.in_(["sticker"]))
async def echo_functions_sticker(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		if message.content_type == "sticker":
			await message.bot.send_sticker(
				current_ids,
				message.sticker.file_id
			)


@router.message(F.content_type.in_(['contact']))
async def echo_functions_contact(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		first_name = message.contact.first_name
		contact = message.contact.phone_number

		if message.content_type == 'contact':
			await message.bot.send_contact(
				current_ids,
				phone_number=contact,
				first_name=first_name
			)


@router.message(F.content_type.in_(["video_note"]))
async def echo_functions_video_note(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		if message.content_type == "video_note":
			await message.bot.send_video_note(
				current_ids,
				message.video_note.file_id,
			)


@router.message(F.content_type.in_(["document"]))
async def echo_functions_document(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
	user_nickname = user_nickname.fetchone()[0]

	is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
	premium = is_premium.fetchone()

	if premium or premium[0] == 2:
		premium_emodji = '💎'
	else:
		premium_emodji = ''

	nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
	nickname = nickname.fetchone()

	if nickname is not None and nickname[0] is not None:
		message_caption = (f'<b>{user_nickname}{premium_emodji}</b>\n'
	                     f'{message.caption}' if message.caption is not None else f'<b>{user_nickname}</b>\n')
	else:
		message_caption = f'{message.caption}' if message.caption else None

	if status_user == 3:
			if message.content_type == "document":
				await message.bot.send_document(
					current_ids,
					message.document.file_id,
					caption=message_caption
				)


@router.message(F.content_type.in_(["location"]))
async def echo_functions_location(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		if message.content_type == 'location':
			longitude = message.location.longitude
			latitude = message.location.latitude

			await message.bot.send_location(
				current_ids,
				latitude=latitude,
				longitude=longitude,
				protect_content=False
			)


@router.message(F.content_type.in_(["video"]))
async def echo_video(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id)
	)
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		if message.content_type == "video":
			select_hide_videos = await session.execute(select(Connection.connect_user_id).where(Connection.user_id == user_id))
			select_hide_videos = select_hide_videos.fetchone()[0]

			hide_status = await session.execute(select(User.spoiler).where(User.user_id == select_hide_videos))
			hide_status = hide_status.fetchone()[0]

			opponent_view = await session.execute(select(Connection.view_all).where(Connection.user_id == select_hide_videos))
			opponent_view = opponent_view.fetchone()[0] if opponent_view else None

			video = message.video.file_id
			caption = message.caption if message.caption else None

			if hide_status == 1 and opponent_view != 1:
				ten_days_later = datetime.datetime.now() + datetime.timedelta(days=10)
				formatted_time = ten_days_later.strftime("%Y:%m:%d %H:%M:%S")

				path = os.path.join('photos', 'alert.jpg'),
				video_hash = hashlib.md5(video.encode()).hexdigest()

				add_video = Video_user(user_id=current_ids, video_hash=video_hash, video=video, caption=caption, date_time=formatted_time)
				session.add(add_video)
				await session.commit()

				keyboards = await butt_for_show_video(video_hash)

				await message.bot.send_photo(
					current_ids,
					photo=FSInputFile(path),
					reply_markup=keyboards
				)

			elif hide_status != 1 or opponent_view == 1:
				user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
				user_nickname = user_nickname.fetchone()[0]

				is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
				premium = is_premium.fetchone()

				if premium or premium[0] == 2:
					premium_emodji = '💎'
				else:
					premium_emodji = ''

				nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
				nickname = nickname.fetchone()

				if nickname is not None and nickname[0] is not None:
					message_caption = (f'<b>{user_nickname}{premium_emodji}</b>\n'
					                   f'{message.caption}' if message.caption is not None else f'<b>{user_nickname}</b>\n')
				else:
					message_caption = f'{message.caption}' if message.caption else None

				await message.bot.send_video(
					current_ids,
					message.video.file_id,
					caption=message_caption
				)


@router.callback_query(F.data.startswith('view_one_video_'))
async def check_video_1(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	data_call = callback.data.split('_')[3]

	video = await session.execute(select(Video_user.video).where(Video_user.video_hash == data_call))
	video = video.fetchone()[0]

	caption_row = await session.execute(select(Video_user.caption).where(Video_user.video_hash == data_call))
	caption = caption_row.fetchone()[0] if caption_row else None

	await bot.edit_message_media(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		media=InputMediaVideo(
			media=f'{video}',
			caption=caption
		),
	)

	await session.execute(delete(Video_user).where(Video_user.video_hash == data_call))
	await session.commit()


@router.callback_query(F.data.startswith('view_chat_video_'))
async def check_video(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	data_call = callback.data.split('_')[3]
	user_id = callback.from_user.id

	video = await session.execute(select(Video_user.video).where(Video_user.video_hash == data_call))
	video = video.fetchone()[0]

	caption_row = await session.execute(select(Video_user.caption).where(Video_user.video_hash == data_call))
	caption = caption_row.fetchone()[0] if caption_row else None

	await session.execute(update(Connection).where(Connection.user_id == user_id).values(view_all=1))
	await session.commit()

	await bot.edit_message_media(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		media=InputMediaVideo(
			media=f'{video}',
			caption=caption
		),
	)

	await session.execute(delete(Video_user).where(Video_user.video_hash == data_call))
	await session.commit()


@router.message(F.content_type.in_(["photo"]))
async def echo_photo(message: Message, session: AsyncSession) -> None:
	user_id: int = message.from_user.id

	user = await session.execute(
		select(Search_Connection.search_status).where(Search_Connection.user_id == user_id))
	status_user = user.fetchone()[0]

	current_ids = await session.execute(
		select(Connection.connect_user_id).where(Connection.user_id == user_id))
	current_ids = current_ids.fetchone()[0]

	if status_user == 3:
		if message.content_type == "photo":
			select_hide_photos = await session.execute(select(Connection.connect_user_id).where(Connection.user_id == user_id))
			select_hide_photos = select_hide_photos.fetchone()[0]

			hide_status = await session.execute(select(User.spoiler).where(User.user_id == select_hide_photos))
			hide_status = hide_status.fetchone()[0]

			opponent_view = await session.execute(select(Connection.view_all).where(Connection.user_id == select_hide_photos))
			opponent_view = opponent_view.fetchone()[0] if opponent_view else None

			photo = message.photo[-1].file_id
			caption = message.caption if message.caption else None

			if hide_status == 1 and opponent_view != 1:
				ten_days_later = datetime.datetime.now() + datetime.timedelta(days=10)
				formatted_time = ten_days_later.strftime("%Y:%m:%d %H:%M:%S")

				path = os.path.join('photos', 'alert.jpg'),
				photo_hash = hashlib.md5(photo.encode()).hexdigest()

				add_photo = Photo_user(user_id=current_ids, photo_hash=photo_hash, photo=photo, caption=caption, date_time=formatted_time)
				session.add(add_photo)
				await session.commit()

				keyboards = await butt_for_show_photo(photo_hash)

				await message.bot.send_photo(
					current_ids,
					photo=FSInputFile(path),
					reply_markup=keyboards
				)

			elif hide_status != 1 or opponent_view == 1:
				user_nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
				user_nickname = user_nickname.fetchone()[0]

				is_premium = await session.execute(select(User.is_premium).where(User.user_id == user_id))
				premium = is_premium.fetchone()

				if premium or premium[0] == 2:
					premium_emodji = '💎'
				else:
					premium_emodji = ''

				nickname = await session.execute(select(User.nickname).where(User.user_id == user_id))
				nickname = nickname.fetchone()

				if nickname is not None and nickname[0] is not None:
					message_caption = (f'<b>{user_nickname}{premium_emodji}</b>\n'
					                   f'{message.caption}' if message.caption is not None else f'<b>{user_nickname}</b>\n')
				else:
					message_caption = f'{message.caption}' if message.caption else None

				await message.bot.send_photo(
					current_ids,
					message.photo[-1].file_id,
					caption=message_caption
				)


@router.callback_query(F.data.startswith('view_one_photo_'))
async def check_photo(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	data_call = callback.data.split('_')[3]

	photo = await session.execute(select(Photo_user.photo).where(Photo_user.photo_hash == data_call))
	photo = photo.fetchone()[0]

	caption_row = await session.execute(select(Photo_user.caption).where(Photo_user.photo_hash == data_call))
	caption = caption_row.fetchone()[0] if caption_row else None

	await bot.edit_message_media(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		media=InputMediaPhoto(
			media=f'{photo}',
			caption=caption
		),
	)

	await session.execute(delete(Photo_user).where(Photo_user.photo_hash == data_call))
	await session.commit()


@router.callback_query(F.data.startswith('view_chat_photo_'))
async def check_photo_1(callback: CallbackQuery, bot: Bot, session: AsyncSession) -> None:
	data_call = callback.data.split('_')[3]
	user_id: int = callback.from_user.id

	photo = await session.execute(select(Photo_user.photo).where(Photo_user.photo_hash == data_call))
	photo = photo.fetchone()[0]

	caption_row = await session.execute(select(Photo_user.caption).where(Photo_user.photo_hash == data_call))
	caption = caption_row.fetchone()[0] if caption_row else None

	await session.execute(update(Connection).where(Connection.user_id == user_id).values(view_all=1))
	await session.commit()

	await bot.edit_message_media(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		media=InputMediaPhoto(
			media=f'{photo}',
			caption=caption
		),
	)

	await session.execute(delete(Photo_user).where(Photo_user.photo_hash == data_call))
	await session.commit()