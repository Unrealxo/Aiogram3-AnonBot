import datetime
from typing import Any, Awaitable, Callable, cast

from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.database_postgres import Photo_user, Video_user


class MediaCheckMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker) -> None:
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        message = cast(Update, event)

        async with self.session_pool() as session:
            if message and message.message and message.message.from_user:
                user_id = message.message.from_user.id

                ten_days_later = datetime.datetime.now()
                formatted_time = ten_days_later.strftime("%Y:%m:%d %H:%M:%S")

                choose_photos = await session.execute(
                    select(Photo_user)
                    .where(Photo_user.date_time <= formatted_time)
                    .where(Photo_user.user_id == user_id)
                )
                records_to_delete = choose_photos.scalars().all()

                for record in records_to_delete:
                    await session.delete(record)
                await session.commit()

                ten_days_later_video = datetime.datetime.now()
                formatted_time = ten_days_later_video.strftime("%Y:%m:%d %H:%M:%S")

                choose_viedos = await session.execute(
                    select(Video_user)
                    .where(Video_user.date_time <= formatted_time)
                    .where(Video_user.user_id == user_id)
                )
                records_to_delete2 = choose_viedos.scalars().all()

                for record2 in records_to_delete2:
                    await session.delete(record2)
                await session.commit()

            return await handler(message, data)