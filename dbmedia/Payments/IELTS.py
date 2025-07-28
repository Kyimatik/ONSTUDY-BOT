from aiogram import Router, F
from aiogram.types import (
    CallbackQuery, Message, LabeledPrice, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from ..bot_instance import bot
from dotenv import load_dotenv
import aiogram 
import os, logging
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from buttons import basic, standart, premium
from dbmedia.session import get_db
from dbmedia.models import User, Subscription, Course # импорт Subscription

load_dotenv("onstudy.env")
LIVE_TOKEN = os.getenv("LIVE_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_ID"))


router = Router()  # IELTS Router 


@router.callback_query(lambda c: c.data == "ielts")
async def choose_range(callback: CallbackQuery):
    async with get_db() as db:
        result = await db.execute(
                select(Course)
                .where(Course.id == 1)
            )
        course = result.scalars().first()
        # if course.isFinished == False:
        #     await callback.message.answer("Курс в разработке.")
        #     return 
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Basic", callback_data="buy_basic")],
        [InlineKeyboardButton(text="Standart", callback_data="buy_standart")],
        [InlineKeyboardButton(text="Premium", callback_data="buy_premium")]
    ])
    await callback.message.answer("Выберите тариф:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("buy_"))
async def choose_tariff(callback: CallbackQuery):
    tariff = callback.data.split("_")[1]
    reply_markup = {
        "basic": basic,
        "standart": standart,
        "premium": premium
    }.get(tariff)

    # Жадно подгружаем подписки вместе с пользователем
    async with get_db() as db:
        result = await db.execute(
            select(User)
            .where(User.tg_id == callback.from_user.id)
            .options(selectinload(User.subscriptions))
        )
        user = result.scalars().first()

        active_sub = None
        if user:
            for sub in user.subscriptions:
                if sub.is_active and sub.course_id == 1 and  sub.expired_date and sub.expired_date > datetime.utcnow():
                    active_sub = sub
                    break
        
        print(active_sub)
        

        if active_sub and active_sub.sub_type != tariff:
            await callback.message.answer(
                "❌ Вы не можете сменить тариф до окончания текущей подписки.\n"
                "Сейчас вы можете только продлить свой тариф."
            )
            return

    if reply_markup:
        await callback.message.answer("На сколько хотите подписку?", reply_markup=reply_markup)
    else:
        await callback.message.answer("Неверный тариф")


@router.callback_query(lambda c: c.data and c.data.startswith("mon"))
async def choose_tariff_length(callback: CallbackQuery):
    user_id = callback.from_user.id
    term = callback.data  # например "month_basic"
    tariff = term.split("_")[1]

    price_map = {
        "month_basic": LabeledPrice(label="Basic", amount=300_000),
        "month3_basic": LabeledPrice(label="Basic", amount=765_000),
        "month_standart": LabeledPrice(label="Standart", amount=350_000),
        "month3_standart": LabeledPrice(label="Standart", amount=895_000),
        "month_premium": LabeledPrice(label="Premium", amount=500_000),
        "month3_premium": LabeledPrice(label="Premium", amount=1_250_000),
    }

    price = price_map.get(term)
    if not price:
        await callback.message.answer("Неизвестный тариф")
        return

    clean_tar, _ = term.split("_")  # "month" или "month3"

    await bot.send_invoice(
        chat_id=user_id,
        title=f"Покупка тарифа {tariff.capitalize()}",
        description=f"Оплата тарифа {tariff.capitalize()}",
        provider_token=LIVE_TOKEN,
        currency="KGS",
        prices=[price],
        start_parameter=f"buy_{tariff}",
        payload=f"{clean_tar}_{tariff}_{user_id}_IELTS_1",
        need_phone_number=True,
        need_email=True,
        send_phone_number_to_provider=True,
        send_email_to_provider=True
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as e:
        logging.warning(f"Ошибка при подтверждении оплаты: {e}")


