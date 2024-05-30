from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select, update, delete

from State.state_reg import Register_anketa
from database.database_postgres import (async_session, UserCaptcha,
                                        UserCaptchaConfirm, Search_Connection,
                                        User)
from keyboard.inline.captcha_kb import captcha_kb
from keyboard.inline.register_kb import choose_gender

router = Router()


@router.callback_query(F.data.startswith('emodji_'))
async def call_froms(callback: CallbackQuery, bot: Bot, state: FSMContext,
                     session: async_session) -> None:
    """
    Проверка пользователя на анти-бота
    внутренняя структура проверки
    и переход к регистрации пользователя.
    """
    user_id: int = callback.from_user.id

    # Не проводим проверку если пользователь уже присутствует в базе данных.
    select_user = await session.execute(select(UserCaptchaConfirm).filter_by(user_id=user_id))
    select_user = select_user.fetchone()
    if select_user is not None:
        return

    # Инициализация эмодзи между пользователем и ботом.
    emoji_to_english = {
        "⭐": "star", "♥️": "heart", "🍄": "mushroom", "🔥": "fire",
        "⚽": "soccer_ball", "🏆": "trophy", "🍎": "apple", "🌍": "earth",
        "🍪": "cookie", "🧭": "compass", "🌼": "flower", "🎲": "dice"
    }

    # Получаем информацию с функции captcha_kb, inline.captcha_kb.
    ikb, dict_for_emodji = await captcha_kb()
    emodji_from_user: int = int(callback.data.split('_')[1])

    # Распаковываем словарь и получаем эмодзи.
    dict_for_emodji = dict_for_emodji['random_4_emodji']

    # Выводим каждый статус пользователя из базы данных.
    status1 = await session.execute(select(UserCaptcha.status1).filter_by(user_id=user_id))
    user1_result = status1.fetchone()
    if user1_result[0] == 1:
        user1 = 1
    else:
        user1 = 0
    status2 = await session.execute(select(UserCaptcha.status2).filter_by(user_id=user_id))
    user2_result = status2.fetchone()
    if user2_result[0] == 1:
        user2 = 1
    else:
        user2 = 0
    status3 = await session.execute(select(UserCaptcha.status3).filter_by(user_id=user_id))
    user3_result = status3.fetchone()
    if user3_result[0] == 1:
        user3 = 1
    else:
        user3 = 0
    status4 = await session.execute(select(UserCaptcha.status4).filter_by(user_id=user_id))
    user4_result = status4.fetchone()
    if user4_result[0] == 1:
        user4 = 1
    else:
        user4 = 0

    # Добавляем пользователя во временную базу данных для регистрации.
    select_user = await session.execute(select(UserCaptcha).filter_by(user_id=user_id))
    select_user = select_user.fetchone()

    if select_user is None:
        new_user = UserCaptcha(user_id=user_id)
        session.add(new_user)
        await session.commit()

    # Если статусы равны 0, то вызываем первую проверку.
    if user1 + user2 + user3 + user4 == 0:
        user_captcha = await session.execute(select(UserCaptcha.emodji).filter_by(user_id=user_id))
        user_captcha = user_captcha.fetchone()[0]
        user_captcha = user_captcha.split(',')[0]

        if user_captcha == "star":
            user_captcha = "⭐"
        elif user_captcha == "heart":
            user_captcha = "♥️"
        elif user_captcha == "mushroom":
            user_captcha = "🍄"
        elif user_captcha == "fire":
            user_captcha = "🔥"
        elif user_captcha == "soccer_ball":
            user_captcha = "⚽"
        elif user_captcha == "trophy":
            user_captcha = "🏆"
        elif user_captcha == "apple":
            user_captcha = "🍎"
        elif user_captcha == "earth":
            user_captcha = "🌍"
        elif user_captcha == "cookie":
            user_captcha = "🍪"
        elif user_captcha == "compass":
            user_captcha = "🧭"
        elif user_captcha == "flower":
            user_captcha = "🌼"
        elif user_captcha == "dice":
            user_captcha = "🎲"

        # Если call_data от пользователя == эмодзи, то пропускаем.
        if emodji_from_user == user_captcha:
            # Ставим статус на вторую проверку то есть status1 = 1.
            await session.execute(update(UserCaptcha).where(UserCaptcha.user_id == user_id).values(status1=1))
            await session.commit()

            await callback.answer(text="Первый верный!")
        else:
            # Отправка новой проверки, если пользователь ошибся.
            await callback.answer(text="❌ Неверно!" )
            # Удаляет временную базу данных.
            await session.execute(delete(UserCaptcha).where(UserCaptcha.user_id == user_id))
            await session.commit()

            # Перемешиваем эмодзи для ноовй проверки.
            english_emodji = [emoji_to_english[char] for char in dict_for_emodji]
            emodji_str = ', '.join(english_emodji)

            # Создаём временную БД.
            user_captcha = UserCaptcha(user_id=user_id, emodji=emodji_str)
            session.add(user_captcha)
            await session.commit()

            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=f"🤖 Анти-бот система\n\n"
                     f"<b>Выбирай значения ниже в таком же порядке!</b>\n\n"
                     f"{' ⮕  '.join(dict_for_emodji)}",
                reply_markup=ikb
            )

    # Проверка на второй статус. И так далее до завершения 4 проверки.
    if user1 + user2 + user3 + user4 == 1:
        user_captcha = await session.execute(select(UserCaptcha.emodji).filter_by(user_id=user_id))
        user_captcha = user_captcha.fetchone()[0]
        user_captcha = user_captcha.split(',')[1].strip()

        if user_captcha == "star":
            user_captcha = "⭐"
        elif user_captcha == "heart":
            user_captcha = "♥️"
        elif user_captcha == "mushroom":
            user_captcha = "🍄"
        elif user_captcha == "fire":
            user_captcha = "🔥"
        elif user_captcha == "soccer_ball":
            user_captcha = "⚽"
        elif user_captcha == "trophy":
            user_captcha = "🏆"
        elif user_captcha == "apple":
            user_captcha = "🍎"
        elif user_captcha == "earth":
            user_captcha = "🌍"
        elif user_captcha == "cookie":
            user_captcha = "🍪"
        elif user_captcha == "compass":
            user_captcha = "🧭"
        elif user_captcha == "flower":
            user_captcha = "🌼"
        elif user_captcha == "dice":
            user_captcha = "🎲"

        if emodji_from_user == user_captcha:
            await session.execute(update(UserCaptcha).where(UserCaptcha.user_id == user_id).values(status2=1))
            await session.commit()

            await callback.answer(text="Второй верный!")
        else:
            await callback.answer(text="❌ Неверно!")

            await session.execute(delete(UserCaptcha).where(UserCaptcha.user_id == user_id))
            await session.commit()

            english_emodji = [emoji_to_english[char] for char in dict_for_emodji]
            emodji_str = ', '.join(english_emodji)

            user_captcha = UserCaptcha(user_id=user_id, emodji=emodji_str)
            session.add(user_captcha)
            await session.commit()

            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=f"🤖 Анти-бот система\n\n"
                     f"<b>Выбирай значения ниже в таком же порядке!</b>\n\n"
                     f"{' ⮕  '.join(dict_for_emodji)}",
                reply_markup=ikb
            )
    elif user1 + user2 + user3 + user4 == 2:
        user_captcha = await session.execute(select(UserCaptcha.emodji).filter_by(user_id=user_id))
        user_captcha = user_captcha.fetchone()[0]
        user_captcha = user_captcha.split(',')[2].strip()

        if user_captcha == "star":
            user_captcha = "⭐"
        elif user_captcha == "heart":
            user_captcha = "♥️"
        elif user_captcha == "mushroom":
            user_captcha = "🍄"
        elif user_captcha == "fire":
            user_captcha = "🔥"
        elif user_captcha == "soccer_ball":
            user_captcha = "⚽"
        elif user_captcha == "trophy":
            user_captcha = "🏆"
        elif user_captcha == "apple":
            user_captcha = "🍎"
        elif user_captcha == "earth":
            user_captcha = "🌍"
        elif user_captcha == "cookie":
            user_captcha = "🍪"
        elif user_captcha == "compass":
            user_captcha = "🧭"
        elif user_captcha == "flower":
            user_captcha = "🌼"
        elif user_captcha == "dice":
            user_captcha = "🎲"

        if emodji_from_user == user_captcha:
            await session.execute(update(UserCaptcha).where(UserCaptcha.user_id == user_id).values(status3=1))
            await session.commit()

            await callback.answer(text="Третий верный!")
        else:
            await callback.answer(text="❌ Неверно!")

            await session.execute(delete(UserCaptcha).where(UserCaptcha.user_id == user_id))
            await session.commit()

            english_emodji = [emoji_to_english[char] for char in dict_for_emodji]
            emodji_str = ', '.join(english_emodji)

            user_captcha = UserCaptcha(user_id=user_id, emodji=emodji_str)
            session.add(user_captcha)
            await session.commit()

            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=f"🤖 Анти-бот система\n\n"
                     f"<b>Выбирай значения ниже в таком же порядке!</b>\n\n"
                     f"{' ⮕  '.join(dict_for_emodji)}",
                reply_markup=ikb
            )
    elif user1 + user2 + user3 + user4 == 3:
        user_captcha = await session.execute(select(UserCaptcha.emodji).filter_by(user_id=user_id))
        user_captcha = user_captcha.fetchone()[0]
        user_captcha = user_captcha.split(',')[3].strip()

        if user_captcha == "star":
            user_captcha = "⭐"
        elif user_captcha == "heart":
            user_captcha = "♥️"
        elif user_captcha == "mushroom":
            user_captcha = "🍄"
        elif user_captcha == "fire":
            user_captcha = "🔥"
        elif user_captcha == "soccer_ball":
            user_captcha = "⚽"
        elif user_captcha == "trophy":
            user_captcha = "🏆"
        elif user_captcha == "apple":
            user_captcha = "🍎"
        elif user_captcha == "earth":
            user_captcha = "🌍"
        elif user_captcha == "cookie":
            user_captcha = "🍪"
        elif user_captcha == "compass":
            user_captcha = "🧭"
        elif user_captcha == "flower":
            user_captcha = "🌼"
        elif user_captcha == "dice":
            user_captcha = "🎲"

        if emodji_from_user == user_captcha:
            await session.execute(update(UserCaptcha).where(UserCaptcha.user_id == user_id).values(status4=1))
            await callback.answer(text="Четвертый верный!")

            await session.execute(delete(UserCaptcha).where(UserCaptcha.user_id == user_id))
            new_user = UserCaptchaConfirm(user_id=user_id)
            session.add(new_user)

            new_user_search = Search_Connection(user_id=user_id, search_status=1, gender=1, interests=1)
            session.add(new_user_search)

            await session.execute(update(User).where(User.user_id == user_id).values(spoiler=1))
            await session.commit()

            # Обрабатываем если пользователя прошёл регистрацию на АНТИ-БОТ.
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="Успешно пройдено!"
            )

            # Меняем статус пользователя на выбор анкет, а также отправляем диалоговое окно
            # с выбором пола ( inline.register_kb ).
            pol = await choose_gender()
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="🤖 Выбери свой пол:",
                reply_markup=pol
            )
            await state.set_state(Register_anketa.gender)
        else:
            await callback.answer(text="❌ Неверно!"  )

            select_user2 = await session.execute(select(UserCaptcha).filter_by(user_id=user_id))
            select_user2 = select_user2.fetchone()

            if select_user2:
                await session.execute(delete(UserCaptcha).where(UserCaptcha.user_id == user_id))
                await session.commit()

            english_emodji = [emoji_to_english[char] for char in dict_for_emodji]
            emodji_str = ', '.join(english_emodji)

            user_captcha = UserCaptcha(user_id=user_id, emodji=emodji_str)
            session.add(user_captcha)
            await session.commit()

            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=f"🤖 Анти-бот система\n\n"
                     f"<b>Выбирай значения ниже в таком же порядке!</b>\n\n"
                     f"{' ⮕  '.join(dict_for_emodji)}",
                reply_markup=ikb
            )