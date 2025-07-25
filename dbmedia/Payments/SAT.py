from aiogram import Router, types, F
from aiogram.types import (
    CallbackQuery, Message, LabeledPrice, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from ..bot_instance import bot
from dotenv import load_dotenv
import os
import logging
from sqlalchemy.future import select
from sqlalchemy import and_
from buttons import basic, standart, premium, StartButtonOfPayments
from ..session import get_db
from ..models import User
from datetime import datetime, timedelta




from aiogram.types import ChatInviteLink

load_dotenv("onstudy.env")
LIVE_TOKEN = os.getenv("LIVE_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_ID"))

router = Router() # SAT Router