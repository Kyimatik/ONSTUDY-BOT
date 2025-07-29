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
from .models import User, Subscription
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta
import os 
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
        


# @router.message(Command("account"))
# async def getDataAbtUser(message: Message):
#     user_id = message.from_user.id
#     async with get_db() as db:
#         stmt = select(User).where(User.tg_id == user_id)
#         result = await db.execute(stmt)
#         user = result.scalars().first()
#         if user:
#             await message.answer(f"""Подписка - {user.sub_type} 
# Срок подписки - {user.expired_date}
# """)
#         else:
#             await message.answer("Вы не покупали подписку")

# Крон для группы Эссе
async def CronFuncDeleteEssay():
    async with get_db() as db:
        stmt = select(Subscription).where(Subscription.course_id == 3)
        res = await db.execute(stmt)
        subs = res.scalars().all() # Все подписки 
        if subs is None:
            return 
        for i in subs:
            try:
                stmtForUser = select(User).where(User.tg_id == i.user_id) # сам SQL Заппрос 
                resForUesr = await db.execute(stmtForUser) # сам Execute
                user = resForUesr.scalars().first() # Первый пользователь 
                res = await bot.get_chat_member(chat_id, user.tg_id)
                if res.status == "member":
                    await bot.ban_chat_member(chat_id=chat_id, user_id=i)
                    await db.delete(i)
                    await db.commit()
                    logging.info(f"Пользователь {i}|{res.user.username}")
                else:   
                    continue
            except Exception as e:
                logging.warning(f"Произошла ошибка при удалении пользователя - {e}")
            finally:
                continue
    

    



