from .session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert, update, delete
from .models import User



# Функция для получения всех user_id
async def get_all_users(session: AsyncSession) -> list[int]:
    result = await session.execute(select(User.user_id).distinct())
    return [row[0] for row in result.all()]

# Добавление пользователя
async def add_user(session: AsyncSession, user_id: int) -> bool:
    new_user = User(user_id=user_id)
    session.add(new_user)
    try:
        await session.flush()  
        return True
    except IntegrityError:
        await session.rollback()
        return False







    