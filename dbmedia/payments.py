from aiogram import Router,types, F 
from aiogram.types import CallbackQuery, Message,LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .bot_instance import dp,bot
from dotenv import load_dotenv 
import os 

load_dotenv("onstudy.env")


LIVE_TOKEN = os.getenv("LIVE_TOKEN")


router = Router()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

@router.message(Command("buy"))
async def choose_tariff(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Standart - 7 KGS", callback_data="buy_standart")],
        [InlineKeyboardButton(text="Individual - 8 KGS", callback_data="buy_individual")],
        [InlineKeyboardButton(text="Premium - 9 KGS", callback_data="buy_premium")]
    ])
    await message.answer("Выберите тариф:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("buy_"))
async def process_tariff_selection(callback_query: CallbackQuery):
    tariff = callback_query.data.split("_")[1]
    if tariff == "standart":
        prices = [LabeledPrice(label="Standart", amount=700)] # Цена  = 1 эквивалент * на 100
    elif tariff == "individual":
        prices = [LabeledPrice(label="Individual", amount=800)]
    elif tariff == "premium":
        prices = [LabeledPrice(label="Premium", amount=900)]
    else:
        await callback_query.answer("Неизвестный тариф")
        return

    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=f"Покупка тарифа {tariff.capitalize()}",
        description=f"Оплата тарифа {tariff.capitalize()}",
        provider_token=f"{LIVE_TOKEN}",
        currency="KGS",
        prices=prices,
        start_parameter=f"buy_{tariff}",
        payload=f"payload_{tariff}"
    )
    await callback_query.answer()



@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery) -> None:
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as e:
        print("Error in pre_checkout_query:", e)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    payment_info = message.successful_payment
    transaction_id = payment_info.telegram_payment_charge_id

    await message.answer("Спасибо за покупку!")