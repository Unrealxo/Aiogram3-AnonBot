from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.database_postgres import UserCaptchaConfirm, UserCaptcha
from keyboard.inline.captcha_kb import captcha_kb


class CaptchaFilter(BaseFilter):
	"""
	Инициализация с базой данный для поддержания

	асинхроного воздействия на код.
	"""
	def __init__(self, session_pool: async_sessionmaker) -> None:
		super().__init__()
		self.session_pool = session_pool

	async def __call__(self, message: Message, bot: Bot) -> bool:
		"""
		Проверка пользователя на анти-бот.

		если есть в базе данных -> Проталкиваем handler

		нету -> Выдаём инициализацию прохождения капчи.
		"""
		async with self.session_pool() as session:
			user_id = message.from_user.id
			# Если пользователя с этим пунктом нет в БД, даём ему капчу.
			# Есть -> проталкиваем хендлер
			select_user = await session.execute(select(UserCaptchaConfirm).filter_by(user_id=user_id))
			select_user = select_user.fetchone()

			if select_user is None:
				# Удаляем временную бд во избежание ошибок с id пользователя.
				await session.execute(delete(UserCaptcha).where(UserCaptcha.user_id == user_id))
				await session.commit()

				# получаем данный с ( inline.captcha_kb )
				ikb, dict_for_emodji = await captcha_kb()
				random_4_emodji = dict_for_emodji['random_4_emodji']

				# Эмодзи для заноса в БД
				emoji_to_english = {
					"⭐": "star", "♥️": "heart", "🍄": "mushroom",
					"🔥": "fire", "⚽": "soccer_ball", "🏆": "trophy",
					"🍎": "apple", "🌍": "earth", "🍪": "cookie",
					"🧭": "compass", "🌼": "flower", "🎲": "dice"
				}

				english_emodji = [emoji_to_english[char] for char in random_4_emodji]
				emodji_str = ', '.join(english_emodji)

				# Создаём временную БД
				user_captcha = UserCaptcha(user_id=user_id, emodji=emodji_str)
				session.add(user_captcha)
				await session.commit()

				# Чтобы не засорялся чат.
				# Удаляем ненужные сообщения со стороны бота и user'а
				if message == '/start':
					pass
				else:
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
						print(f'{e}, ошибка удаления. Несущественно')

				await message.bot.send_message(
					chat_id=message.chat.id,
					text=f"🤖 Анти-бот система\n\n"
					     f"<b>Выбирай значения ниже в таком же порядке!</b>\n\n"
					     f"{' ⮕  '.join(random_4_emodji)}",
					reply_markup=ikb
				)
				return False
			return True

