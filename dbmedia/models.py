from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Integer, Boolean, BigInteger, Column, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR
from sqlalchemy.ext.mutable import MutableList

from .session import Base




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, index=True)

    session_id = Column(String, unique=True, index=True, nullable=True)
    session_created_at = Column(DateTime, nullable=True)

    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")   


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    isFinished = Column(Boolean, nullable=True)

    modules = relationship(
        "CourseModule",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    subscriptions = relationship("Subscription", back_populates="course", cascade="all, delete-orphan")

    class Config:
        orm_mode = True



class CourseModule(Base):
    __tablename__ = "course_modules"

    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    
    course = relationship("Course", back_populates="modules")

    
    lessons = relationship(
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    
    module_id = Column(Integer, ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=False)
    module = relationship("CourseModule", back_populates="lessons")

    order = Column(Integer, nullable=True)
    video_link = Column(String, nullable=False)
    description = Column(String, nullable=True)
    video_cover = Column(String, nullable=True)
    isTest = Column(Boolean, nullable=True)
    isNotes = Column(Boolean, nullable=True)




class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    title = Column(String, nullable=False)
    count_of_slots = Column(Integer, nullable=False)
    registered_users = Column(MutableList.as_mutable(ARRAY(VARCHAR)), default=list)



    def __repr__(self):
        return f"<Appointment(id={self.id}, date={self.date}, time={self.time}, title='{self.title}', count_of_slots={self.count_of_slots})>"



class TgUsers(Base):
    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(BigInteger, unique=True, nullable=False)
    joinDate = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<TgUser tg_user_id={self.tg_user_id} joined_at={self.join_date}>"


# Модель подписки 
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    sub_type = Column(String)

    purchase_date = Column(DateTime, default=datetime.utcnow)
    expired_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions")
    course = relationship("Course", back_populates="subscriptions")
