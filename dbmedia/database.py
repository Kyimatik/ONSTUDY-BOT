from dbmedia.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert, update, delete
from dbmedia.models import TgUsers
import logging 


# Функция для получения всех user_id
async def get_all_users(session: AsyncSession) -> list[int]:
    result = await session.execute(select(TgUsers.userId).distinct())
    return [row[0] for row in result.all()]

# Добавление пользователя
async def add_user(session: AsyncSession, user_id: int) -> bool:
    new_user = TgUsers(userId=user_id)
    session.add(new_user)
    try:
        await session.flush()
        await session.commit()
        return True
    except IntegrityError as e:
        logging.warning(f"[add_user] IntegrityError: {e}")
        await session.rollback()
        return False







    