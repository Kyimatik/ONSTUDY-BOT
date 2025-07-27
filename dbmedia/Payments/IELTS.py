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
from dbmedia.models import User, Subscription  # импорт Subscription

load_dotenv("onstudy.env")
LIVE_TOKEN = os.getenv("LIVE_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_ID"))
course_id = int(os.getenv("IELTS_ID"))

router = Router()  # IELTS Router 


@router.callback_query(lambda c: c.data == "ielts")
async def choose_range(callback: CallbackQuery):
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
                if sub.is_active and sub.expired_date and sub.expired_date > datetime.utcnow():
                    active_sub = sub
                    break

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
        payload=f"{clean_tar}_{tariff}_{user_id}_IELTS",
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


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    user_id = message.from_user.id
    payment = message.successful_payment
    today = datetime.utcnow()

    try:
        clean_tar, tariff, _ = payment.invoice_payload.split("_")
    except Exception:
        await message.answer("Ошибка в структуре платежа.")
        return

    TARIFF_DURATION = {
        ("basic", "month"): 30,
        ("basic", "month3"): 90,
        ("standart", "month"): 30,
        ("standart", "month3"): 90,
        ("premium", "month"): 30,
        ("premium", "month3"): 90,
    }

    days = TARIFF_DURATION.get((tariff, clean_tar))
    if not days:
        await message.answer("Ошибка: не удалось распознать тариф.")
        return

    

    async with get_db() as db:
        result = await db.execute(select(User).where(User.tg_id == user_id))
        user = result.scalars().first()

        if not user:
            user = User(tg_id=user_id)
            db.add(user)
            await db.flush()

        stmt_sub = select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.course_id == course_id,
            Subscription.sub_type == tariff,
            Subscription.is_active == True,
            Subscription.expired_date > today
        )
        result_sub = await db.execute(stmt_sub)
        subscription = result_sub.scalars().first()

        if subscription:
            subscription.expired_date += timedelta(days=days)
            subscription.purchase_date = today
        else:
            subscription = Subscription(
                user_id=user.id,
                course_id=course_id,
                sub_type=tariff,
                purchase_date=today,
                expired_date=today + timedelta(days=days),
                is_active=True
            )
            db.add(subscription)

        await db.commit()

    try:
        await bot.unban_chat_member(chat_id=GROUP_CHAT_ID, user_id=user_id)
    except aiogram.exceptions.TelegramBadRequest as e:
        if "can't remove chat owner" in str(e):
            # Игнорируем ошибку, пользователь — владелец, не нужно разблокировать
            logging.info(f"Пользователь {user_id} — владелец чата, пропускаем unban")
    else:
        raise

    await message.answer("✅ Спасибо за покупку!")
    await message.answer(
        "Уникальная ссылка для вхождения в группу.\n"
        "По ней можно зайти только один раз, и не вздумайте передавать ее другим."
    )
    invite = await bot.create_chat_invite_link(chat_id=GROUP_CHAT_ID, member_limit=1)
    await message.answer(invite.invite_link)
    logging.info(f"Оплата прошла успешно от {user_id}. Тариф: {tariff}")
