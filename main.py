import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from admin_panel import admin_users
from database.database_postgres import async_main, async_session, database_main
from handlers import start, captcha_antibot, register_anketa, settings, choose_connection, content_types, user_commands, \
    settings_hide, gender_search, interests_search, send_link, alertings
from middleware.MediaCheck_middleware import MediaCheckMiddleware
from middleware.Session_middleware import DbSessionMiddleware

TOKEN = ('TOKEN')

async def main() -> None:
    # Подключение к базе данных и создание столбцов, если не созданы.
    await database_main()

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logging.basicConfig(level=logging.INFO)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Подключение Middleware на постоянной основе.
    dp_session_middleware = DbSessionMiddleware(session_pool=async_session)
    dp.update.middleware(dp_session_middleware)

    dp_mediacheck_middleware = MediaCheckMiddleware(session_pool=async_session)
    dp.update.middleware(dp_mediacheck_middleware)

    dp.include_routers(
        start.router,
        captcha_antibot.router,
        register_anketa.router,
        choose_connection.router,
        alertings.router,
        settings.router,
        user_commands.router,
        send_link.router,
        admin_users.router,
        settings_hide.settings_router,
        gender_search.router,
        interests_search.router,
        content_types.router
    )

    # Избавляемся от ненужных обновлений после рестарта бота.
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot Stopped.')