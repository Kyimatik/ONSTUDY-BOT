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
from .models import User
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta
import os 
from dotenv import load_dotenv
import logging 


router = Router()  # Создаем отдельный роутер


load_dotenv("onstudy.env")


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
        


@router.message(Command("account"))
async def getDataAbtUser(message: Message):
    user_id = message.from_user.id
    async with get_db() as db:
        stmt = select(User).where(User.tg_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            await message.answer(f"""Подписка - {user.sub_type} 
Срок подписки - {user.expired_date}
""")
        else:
            await message.answer("Вы не покупали подписку")



async def testFunc():
    chat_id = -1002741216292

    async with get_db() as db:
        stmt = select(User)
        result = await db.execute(stmt)
        users = result.scalars().all()
        listOfId = [i.tg_id for i in users]
        new_list = []

        for i in listOfId:
            try:
                member = await bot.get_chat_member(chat_id=chat_id, user_id=i)
                if member.status == 'member':
                    new_list.append(i)
            except Exception as e:
                logging.warning(f"Не удалось получить участника {i}: {e}")
        
        for i in new_list:
            res = await db.execute(select(User).where(User.tg_id == i))
            user = res.scalars().first()

            if user and user.expired_date is not None:
                if user.expired_date <= datetime.utcnow():
                    try:
                        await bot.ban_chat_member(chat_id, i)
                        await bot.unban_chat_member(chat_id, i)
                        user.expired_date = None
                        await db.commit()
                        logging.info(f"❌ Пользователь {user.tg_id} удалён из {chat_id}")
                    except Exception as e:
                        logging.warning(f"Ошибка при удалении пользователя {i}: {e}")
