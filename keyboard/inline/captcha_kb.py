import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def captcha_kb() -> any:

	"""
	Inline Клавиатура для каптчи\\

	Пагинация инлайн кнопок с эмодзи\\

	Логистика выстроения эмодзи.
	"""
	emodji = [
		"⭐", "♥️", "🍄", "🔥", "⚽", "🏆",
		"🍎", "🌍", "🍪", "🧭", "🌼", "🎲"
	]

	random.shuffle(emodji)
	emodji_choose = emodji[:12]

	random_4_emodji = random.sample(emodji_choose, 4)
	# Словарь для заноса эмодзи.
	dict_for_emodji = {'random_4_emodji': random_4_emodji}

	inline = []
	row = []
	message_count = 0

	for x in emodji_choose:
		# Перебираем для каждого эмодзи свой айди и заносим в клавиатуру
		button = InlineKeyboardButton(text=x, callback_data=f"emodji_{x}")
		row.append(button)
		message_count += 1
		# если в ряду больше 4 кнопок, то делаем новый ряд
		if message_count % 4 == 0:
			inline.append(row)
			row = []

	ikb = InlineKeyboardMarkup(inline_keyboard=inline)

	return ikb, dict_for_emodji
