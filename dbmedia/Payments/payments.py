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

@dp.message(F.successful_payment)
async def on_payment(message: Message):
    user_id = message.from_user.id
    pay = message.successful_payment
    today = datetime.utcnow()

    # 1) Распаковываем payload
    try:
        clean_tar, tariff, _, courseName, course_id_str = pay.invoice_payload.split("_")
        course_id = int(course_id_str)
    except ValueError:
        await message.answer("❌ Неверный payload, повторите платёж.")
        return

    # 2) Длительность тарифа
    DURATION = {
      ("basic","month"): 30, ("basic","month3"): 90,
      ("standart","month"):30,("standart","month3"):90,
      ("premium","month"):30,("premium","month3"):90,
    }
    days = DURATION.get((tariff, clean_tar))
    if not days:
        await message.answer("❌ Не удалось распознать тариф.")
        return

    # 3) Обновляем или создаём подписку
    async with get_db() as db:
        res = await db.execute(select(User).where(User.tg_id==user_id))
        user = res.scalars().first()
        if not user:
            user = User(tg_id=user_id)
            db.add(user)
            await db.flush()

        stmt = select(Subscription).where(
            Subscription.user_id==user.id,
            Subscription.course_id==course_id,
            Subscription.sub_type==tariff,
            Subscription.is_active==True,
            Subscription.expired_date>today
        )
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            existing.expired_date += timedelta(days=days)
            existing.purchase_date = today
        else:
            sub = Subscription(
                user_id=user.id,
                course_id=course_id,
                sub_type=tariff,
                purchase_date=today,
                expired_date=today+timedelta(days=days),
                is_active=True
            )
            db.add(sub)
        await db.commit()

    # 4) Разблокируем и даём ссылку
    try:
        await bot.unban_chat_member(chat_id=GROUP_CHAT_ID, user_id=user_id)
    except Exception as e:
        logging.warning(f"Unban failed: {e}")

    await message.answer("✅ Спасибо за покупку!")
    link = await bot.create_chat_invite_link(chat_id=GROUP_CHAT_ID, member_limit=1)
    await message.answer(link.invite_link)
    logging.info(f"Платёж: user={user_id}, course={courseName}({course_id}), tariff={tariff}, term={clean_tar}")
