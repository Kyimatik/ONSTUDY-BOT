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
    stmt = select(TgUsers)
    quR = await session.execute(stmt)
    res = quR.scalars().all()
    new_list = [i.userId for i in res]
    if user_id not in new_list:
        new_user = TgUsers(userId=user_id)
        session.add(new_user)
    else:
        return 
    try:
        await session.flush()
        await session.commit()
        return True
    except IntegrityError as e:
        logging.warning(f"[add_user] IntegrityError: {e}")
        await session.rollback()
        return False







    