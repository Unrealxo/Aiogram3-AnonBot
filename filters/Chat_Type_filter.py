from typing import Union

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
	def __init__(self, chat_type: Union[str, list]) -> None:
		self.chat_type = chat_type

	async def __call__(self, message: Message, bot: Bot) -> bool:
		"""
		Если указанный chat_type == chat_type сообщения,
		то -> Проталкиваем обработку сообщение.
		Иначе - возвращаем False
		"""
		if isinstance(self.chat_type, str):
			if message.chat.type != self.chat_type:
				return False
		elif isinstance(self.chat_type, list):
			if message.chat.type not in self.chat_type:
				return False
		return True