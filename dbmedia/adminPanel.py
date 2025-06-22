from aiogram import Router,types, F 
from aiogram.types import CallbackQuery, Message,LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .bot_instance import dp,bot
from dotenv import load_dotenv 
import os 
from .config import Admins

router = Router()

@router.message(Command("admin"))
async def getInfo(message: Message):
    pass


