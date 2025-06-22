from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery ,FSInputFile
from aiogram.fsm.context import FSMContext
from dbmedia.database import  get_all_users, add_user
from dbmedia.media import start_text,allstickersid
from buttons import useridkb,mainkb
from dbmedia.config import Admins
from dbmedia.session import get_db


router = Router()  # Создаем отдельный роутер

# Начало работы  
@router.message(Command("start"))
async def getstarted(message: Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await message.answer_sticker(allstickersid["startstick"],reply_markup=useridkb)
    await message.answer(f"""Привет <b>{user_name}</b>!
{start_text["getstarted"]}""",parse_mode="HTML",reply_markup=mainkb)
    async with get_db() as session:
        added = await add_user(session, message.from_user.id)
        




    
# Узнать количество пользователей
@router.message(F.text.lower() == "кол")
async def getcountofpeople(message: Message):
    userid = message.from_user.id 
    if userid not in Admins :
        await message.answer("Доступ запрещен.")
    else:
        async with get_db() as session:
            user_ids = await get_all_users(session)
            await message.answer(f"{len(user_ids)} - Количество пользователей.")
        





