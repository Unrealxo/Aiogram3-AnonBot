from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import admin_users_ids



class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Optional[Message] = None, callback: Optional[CallbackQuery] = None) -> bool:
        if (
                (message and message.from_user.id not in admin_users_ids)
                or
                (callback and callback.message and callback.message.from_user.id not in admin_users_ids)
        ):
            return False
        return True