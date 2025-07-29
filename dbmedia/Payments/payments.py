from aiogram import Router, types, F
from aiogram.types import (
    CallbackQuery, Message, LabeledPrice, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from ..bot_instance import bot, dp
from dotenv import load_dotenv
import os
import logging
from sqlalchemy.future import select
from sqlalchemy import and_
from buttons import basic, standart, premium, StartButtonOfPayments
from ..session import get_db
from ..models import User
from datetime import datetime, timedelta

    


from dbmedia.models import User, Subscription
import logging



from aiogram.types import ChatInviteLink

load_dotenv("onstudy.env")
LIVE_TOKEN = os.getenv("LIVE_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_ID"))

router = Router()








@router.message(Command("buy"))
async def choose_course(message: Message):
    await message.answer("Выберите курс",reply_markup=StartButtonOfPayments)



# Словарь длительностей подписок (ключ: (tariff, term))
DURATION = {
    ("basic", "month"): 30,
    ("basic", "month3"): 90,
    ("standart", "month"): 30,
    ("standart", "month3"): 90,
    ("premium", "month"): 30,
    ("premium", "month3"): 90,
}

@dp.message(F.successful_payment)
async def on_successful_payment(message: Message):
    user_id = message.from_user.id
    pay = message.successful_payment
    today = datetime.utcnow()

    # 1) Разбор payload
    try:
        # Ожидается формат: clean_tar_tariff_ignore_courseName_courseId
        clean_tar, tariff, _, course_name, course_id_str = pay.invoice_payload.split("_")
        course_id = int(course_id_str)
        await message.answer(f"{pay.invoice_payload}")
    except ValueError as e:
        logging.error(f"Ошибка разбора payload: {pay.invoice_payload} - {e}")
        await message.answer("❌ Неверный формат платежных данных (payload). Повторите попытку или свяжитесь с поддержкой.")
        return

    # 2) Проверка длительности тарифа
    days = DURATION.get((tariff, clean_tar))
    if not days:
        logging.error(f"Неизвестный тариф или срок: tariff={tariff}, term={clean_tar}")
        await message.answer("❌ Не удалось распознать тариф или срок подписки. Обратитесь в поддержку.")
        return

    # 3) Работа с базой для создания/обновления подписки
    async with get_db() as db:
        # Получаем пользователя или создаём нового
        result = await db.execute(select(User).where(User.tg_id == user_id))
        user = result.scalars().first()
        if not user:
            user = User(tg_id=user_id)
            db.add(user)
            await db.flush()  # Чтобы user.id стал доступен

        # Ищем активную подписку по курсу и типу тарифа
        stmt = select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.course_id == course_id,
            Subscription.sub_type == tariff,
            Subscription.is_active == True,
            Subscription.expired_date > today
        )
        existing = (await db.execute(stmt)).scalars().first()

        if existing:
            # Продление: если подписка уже истекла, берем сегодня за начало
            if existing.expired_date < today:
                existing.expired_date = today + timedelta(days=days)
            else:
                existing.expired_date += timedelta(days=days)
            existing.purchase_date = today
        else:
            # Создаём новую подписку
            new_sub = Subscription(
                user_id=user.id,
                course_id=course_id,
                sub_type=tariff,
                purchase_date=today,
                expired_date=today + timedelta(days=days),
                is_active=True,
            )
            db.add(new_sub)

        await db.commit()

    # 4) Разбан пользователя в группе (если он был заблокирован)
    try:
        await bot.unban_chat_member(chat_id=GROUP_CHAT_ID, user_id=user_id)
    except Exception as e:
        logging.warning(f"Unban failed for user {user_id}: {e}")

    # 5) Отправляем сообщение и инвайт-ссылку (одноразовую)
    await message.answer(f"✅ Спасибо за покупку! Тариф: {tariff}, Курс: {course_name}")

    try:
        invite_link = await bot.create_chat_invite_link(chat_id=GROUP_CHAT_ID, member_limit=1)
        await message.answer(invite_link.invite_link)
    except Exception as e:
        logging.error(f"Ошибка создания инвайт-ссылки для пользователя {user_id}: {e}")
        await message.answer("⚠️ Не удалось сгенерировать ссылку для доступа, свяжитесь с поддержкой.")

    # Логируем успех
    logging.info(f"Платёж успешно обработан: user_id={user_id}, course={course_name}({course_id}), tariff={tariff}, term={clean_tar}")
    