from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery ,FSInputFile
from aiogram.fsm.context import FSMContext
from dbmedia.database import  get_all_users, add_user
from dbmedia.media import start_text,allstickersid
from buttons import useridkb,mainkb
from dbmedia.config import Admins
from dbmedia.session import get_db
from .bot_instance import bot
from .models import User, Subscription, Course
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta
import os 
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv
import logging 


router = Router()  # Создаем отдельный роутер


load_dotenv("onstudy.env")

logger = logging.getLogger(__name__)

chat_id  = int(os.getenv("GROUP_ID"))

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
        

# 🔹 Helper для получения пользователя с подгруженными подписками и курсами
async def get_user_with_subs(db, tg_id: int):
    result = await db.execute(
        select(User)
        .where(User.tg_id == tg_id)
        .options(
            selectinload(User.subscriptions).selectinload(Subscription.course)
        )
    )
    return result.scalars().first()


# 🔹 Хендлер /account
@router.message(Command("account"))
async def getDataAbtUser(message: Message):
    user_id = message.from_user.id
    async with get_db() as db:
        user = await get_user_with_subs(db, user_id)

        if not user or not user.subscriptions:
            return await message.answer("У вас пока нет активных подписок.")

        sendingStr = ""
        for sub in user.subscriptions:
            sendingStr += f"<b>{sub.course.title}</b>\n{sub.expired_date}\n{sub.sub_type}\n\n"

        await message.answer(sendingStr,parse_mode="HTML")


# 🔹 Крон для группы Эссе
async def CronFuncDeleteEssay():
    async with get_db() as db:
        stmt = (
            select(Subscription)
            .options(selectinload(Subscription.user))
            .where(Subscription.course_id == 3)
        )
        res = await db.execute(stmt)
        subs = res.scalars().all()

        if not subs:
            return

        for sub in subs:
            try:
                user = sub.user
                if not user:
                    continue

                res = await bot.get_chat_member(chat_id, user.tg_id)

                if res.status == "member":
                    await bot.ban_chat_member(chat_id=chat_id, user_id=user.tg_id)
                    await db.delete(sub)
                    await db.commit()
                    logging.info(f"Удалён пользователь {user.tg_id} | @{res.user.username}")
                else:
                    continue

            except Exception as e:
                logging.warning(f"Ошибка при удалении пользователя {sub.id} — {e}")