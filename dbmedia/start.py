from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery ,FSInputFile
from aiogram.fsm.context import FSMContext
from .database import init_db, get_all_users, add_user, get_all_challenge_users
from .media import start_text,allstickersid
from buttons import useridkb,mainkb
from .config import Admins


router = Router()  # Создаем отдельный роутер

# Начало работы  
@router.message(Command("start"))
async def getstarted(message: Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await message.answer_sticker(allstickersid["startstick"],reply_markup=useridkb)
    await message.answer(f"""Привет <b>{user_name}</b>!
{start_text["getstarted"]}""",parse_mode="HTML",reply_markup=mainkb)
    await add_user(user_id)




    
# Узнать количество пользователей
@router.message(F.text.lower() == "кол")
async def getcountofpeople(message: Message):
    userid = message.from_user.id 
    if userid not in Admins :
        await message.answer("Доступ запрещен.")
    else:
        await message.answer(f"{len(await get_all_users())} - Количество пользователей.")
        await message.answer(f"{len(await get_all_challenge_users())} - Количество пользователей. Челлендж")





