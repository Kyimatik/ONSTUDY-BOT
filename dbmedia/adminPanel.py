from aiogram import Router,types, F 
from aiogram.types import CallbackQuery, Message,LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .bot_instance import dp,bot
from dotenv import load_dotenv 
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy import select, insert, update, delete
import os 
from dbmedia.config import Admins
from dbmedia.models import Appointment
from buttons import Cancel
from dbmedia.states import NewAppointment,TitleApp, DateApp, TimeApp, SlotApp

from dbmedia.session import get_db

router = Router()

@router.message(F.text == "X нажми ❌")
async def cancelOperation(message: Message, state: FSMContext):
    async with get_db() as session:
        result = await session.execute(select(Appointment))
        appointments = result.scalars().all()
    keyboard = ReplyKeyboardBuilder()
    
    for appointment in appointments:
        keyboard.button(
            text=f"_{appointment.title}_{appointment.id}"
        )
    keyboard.adjust(3)
    keyboard.button(
        text="Создать"
        )
    await message.answer("Вы отменили действие!",reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.clear()
    return 


@router.message(Command("admin"))
async def getInfo(message: Message):
    if message.from_user.id not in Admins:
        await message.answer("Доступ воспрещен!")
        return 
    async with get_db() as session:
        result = await session.execute(select(Appointment))
        appointments = result.scalars().all()
    keyboard = ReplyKeyboardBuilder()
    
    for appointment in appointments:
        keyboard.button(
            text=f"_{appointment.title}_{appointment.id}"
        )
    keyboard.adjust(3)
    keyboard.button(
        text="Создать"
        )
    await message.answer("🔧 Админ-панель: выбери запись", reply_markup=keyboard.as_markup(resize_keyboard=True))

@router.message(F.text.startswith("_"))
async def editAppointment(message: Message):
    msg = message.text
    msg = msg[::-1]
    indexOfIter = msg.index("_")
    ID = msg[0:indexOfIter]
    appointments = ["Удалить","Название","Дата","Время","Количество","Назад","Посмотреть"]
    if message.from_user.id not in Admins:
        await message.answer("Доступ воспрещен!")
        return 
    keyboard = ReplyKeyboardBuilder()
    for appointment in appointments:
        keyboard.button(
            text=f"{appointment}_{ID}"
        )
    keyboard.adjust(3)
    await message.answer("🔧 Изменить запись", reply_markup=keyboard.as_markup(resize_keyboard=True))

# Кнопка создать
@router.message(F.text == "Создать")
async def editOptionsinMake(message: Message, state : FSMContext):
    await message.answer("Отправьте название новой записи",reply_markup=Cancel)
    await state.set_state(NewAppointment.title)


@router.message(NewAppointment.title)
async def getNewTitle(message: Message, state : FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Отправьте дату новой записи",reply_markup=Cancel)
    await state.set_state(NewAppointment.date)


@router.message(NewAppointment.date)
async def getNewDate(message: Message, state : FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Отправьте время новой записи",reply_markup=Cancel)
    await state.set_state(NewAppointment.time)


@router.message(NewAppointment.time)
async def getNewTime(message: Message, state : FSMContext):
    await state.update_data(time=message.text)
    await message.answer("Отправьте кол-во мест новой записи",reply_markup=Cancel)
    await state.set_state(NewAppointment.slots)


@router.message(NewAppointment.slots)
async def getNewSlots(message: Message, state : FSMContext):
    msg = message.text
    if not msg.isdigit():
        await message.answer("Отправьте еще раз")
        return  # Не забывай return!

    await state.update_data(slots=message.text)
    data = await state.get_data()
    cs = int(data['slots'])

    new_appointment = Appointment(
        title=data['title'],
        date=data['date'],
        time=data['time'],
        count_of_slots=cs
    )

    async with get_db() as session:
        session.add(new_appointment)
        await session.commit()  # ⬅️ Сначала сохраняем в базу

        # Только теперь делаем select — тут уже есть новая запись
        result = await session.execute(select(Appointment))
        appointments = result.scalars().all()

        keyboard = ReplyKeyboardBuilder()
        for appointment in appointments:
            keyboard.button(text=f"_{appointment.title}_{appointment.id}")
        keyboard.adjust(3)
        keyboard.button(text="Создать")

        await message.answer(
            f"""Дата - {new_appointment.date}
Тема - {new_appointment.title}
Время - {new_appointment.time}
Количество человек максимум - {new_appointment.count_of_slots}
""",
            reply_markup=keyboard.as_markup(resize_keyboard=True)
        )
        await state.clear()

    


# Изменение определенной записи
@router.message(F.text.contains("_"))
async def editOptionsinMake(message: Message, state : FSMContext):
    msg = message.text
    msg = msg[::-1] 
    indexOfIter = msg.index("_")
    ID = msg[0:indexOfIter] # ID записи в Базе данных 
    option = msg[indexOfIter+1::]
    option = option[::-1] # Само действие  
    
    if option == "Удалить":
        async with get_db() as session:
            result = await session.execute(select(Appointment).where(Appointment.id == int(ID)))
            appointment = result.scalars().first()
            if appointment:
                await session.delete(appointment)
                await session.commit()
                await message.answer("Успешно удалена запись")
    elif option == "Название":
        await state.update_data(ID=ID)
        await state.set_state(TitleApp.data)
        await message.answer("Отправьте новое название")
    elif option == "Дата":
        await state.update_data(ID=ID)
        await state.set_state(DateApp.data)
        await message.answer("Отправьте новую дату")
    elif option == "Время":
        await state.update_data(ID=ID)
        await state.set_state(TimeApp.data)
        await message.answer("Отправьте новое время")
    elif option == "Количество":
        await state.update_data(ID=ID)
        await state.set_state(SlotApp.data)
        await message.answer("Отправьте новое количество мест")
    elif option == "Посмотреть":
        async with get_db() as session:
            result = await session.execute(select(Appointment).where(Appointment.id == int(ID)))
            appointment = result.scalars().first()
            await message.answer(f"""Дата - {appointment.date}
Тема - {appointment.title}
Время - {appointment.time}
Количество человек максимум - {appointment.count_of_slots}
""")
    elif option == "Назад":
        async with get_db() as session:
            result = await session.execute(select(Appointment))
            appointments = result.scalars().all()
            keyboard = ReplyKeyboardBuilder()
            for appointment in appointments:
                keyboard.button(
                    text=f"_{appointment.title}_{appointment.id}"
                )
            keyboard.adjust(3)
            keyboard.button(
            text="Создать"
            )
            await message.answer("🔧 Админ-панель: выбери запись которую хочешь редачить", reply_markup=keyboard.as_markup(resize_keyboard=True))
# Изменение названия 
@router.message(TitleApp.data)
async def getDate(message: Message, state : FSMContext):
    msg = message.text
    data = await state.get_data() 
    ID = int(data["ID"])
    async with get_db() as session:
        result = await session.execute(select(Appointment).where(Appointment.id == int(ID)))
        appointment = result.scalars().first()
        if appointment:
            appointment.title = msg
            await session.commit()
            await message.answer("Успешно обновлены данные")
            await message.answer(f"""Дата - {appointment.date}
Тема - {appointment.title}
Время - {appointment.time}
Количество человек максимум - {appointment.count_of_slots}
""")
            await state.clear()

# Изменение самой даты 
@router.message(DateApp.data)
async def getDate(message: Message, state : FSMContext):
    msg = message.text
    data = await state.get_data() 
    ID = int(data["ID"])
    async with get_db() as session:
        result = await session.execute(select(Appointment).where(Appointment.id == int(ID)))
        appointment = result.scalars().first()
        if appointment:
            appointment.date = msg
            await session.commit()
            await message.answer("Успешно обновлены данные")
            await message.answer(f"""Дата - {appointment.date}
Тема - {appointment.title}
Время - {appointment.time}
Количество человек максимум - {appointment.count_of_slots}
""")
            await state.clear()

@router.message(TimeApp.data)
async def getDate(message: Message, state : FSMContext):
    msg = message.text
    data = await state.get_data() 
    ID = int(data["ID"])
    
    async with get_db() as session:
        result = await session.execute(select(Appointment).where(Appointment.id == int(ID)))
        appointment = result.scalars().first()
        if appointment:
            appointment.time = msg
            await session.commit()
            await message.answer("Успешно обновлены данные")
            await message.answer(f"""Дата - {appointment.date}
Тема - {appointment.title}
Время - {appointment.time}
Количество человек максимум - {appointment.count_of_slots}
""")
            await state.clear()
        
@router.message(SlotApp.data)
async def getDate(message: Message, state : FSMContext):
    msg = message.text
    data = await state.get_data() 
    ID = int(data["ID"])
    
    async with get_db() as session:
        result = await session.execute(select(Appointment).where(Appointment.id == int(ID)))
        appointment = result.scalars().first()
        if appointment:
            appointment.count_of_slots = msg
            await session.commit()
            await message.answer("Успешно обновлены данные")
            await message.answer(f"""Дата - {appointment.date}
Тема - {appointment.title}
Время - {appointment.time}
Количество человек максимум - {appointment.count_of_slots}
""")
            await state.clear()