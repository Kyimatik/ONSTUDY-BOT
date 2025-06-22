import logging
import sys
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, Update
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv
import uvicorn
import json
import asyncio
import logging
from aiogram.exceptions import TelegramBadRequest
import sys
import aiohttp
from dbmedia.schemas import UserCheck,ChannelCheckResponse

import os

from dotenv import load_dotenv
# импорт всех функций для работы с БД
from dbmedia.database import  get_all_users, add_user
from buttons import Sendall,photoyesorno,buttonsyesorno,confirmationyesorno
from dbmedia.config import Admins
from aiogram import Bot, Dispatcher, Router, types , F 
from aiogram.enums import ParseMode
from aiogram.enums import ContentType
from aiogram.filters import CommandStart , Command
from aiogram.types import Message , CallbackQuery ,FSInputFile
from aiogram.types import ReplyKeyboardMarkup , InlineKeyboardMarkup , InlineKeyboardButton , KeyboardButton , ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import buttons
from aiogram.exceptions import TelegramForbiddenError

from aiogram.enums import ChatMemberStatus

from dbmedia.media import challengeinfo

from dbmedia.states import consult

import aiosqlite



# импорты роутеров
from dbmedia.start import router as startrouter
from dbmedia.callbacks import router as callbackrouter

from dbmedia.payments import router as pay_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from fastapi.middleware.cors import CORSMiddleware




logging.basicConfig(
    level=logging.INFO,  # Теперь записывает DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="OnStudyprep.log",
    filemode="a"
)






# Загружаем переменные окружения
load_dotenv("onstudy.env")

TOKEN = os.getenv("Token")
groupid = os.getenv("groupid")
bdgroupid = os.getenv("bdgroupid")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
CHANNEL_ID = os.getenv("Channel")


# Настройки вебхука
AMOCRM_WEBHOOK_URL = f"https://amojo.amocrm.ru/~external/hooks/telegram?t={TOKEN}"
MAINPATH = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"

# Создаем бота и диспетчер
from dbmedia.bot_instance import bot
from dbmedia.bot_instance import dp


router = Router()

app = FastAPI()




# Webhook-обработчик
@app.post(WEBHOOK_PATH)
async def webhook_handler(request: Request):
    update_data = await request.json()
    
    
    # Конвертируем в объект Update
    telegram_update = Update.model_validate(update_data)
    
    # Передаем обновление диспетчеру
    await dp.feed_update(bot=bot, update=telegram_update)
    
    # Пересылаем запрос в AmoCRM
    async with aiohttp.ClientSession() as session:
        async with session.post(AMOCRM_WEBHOOK_URL, json=update_data) as response:
            amo_response = await response.text()
            logging.info(f"Ответ от AmoCRM: {amo_response}")
    
    return {"ok": True}





@app.get("/")
async def home():
    return {"message": "Bot Webhook is working!"}


@app.post("/user_in_channel",response_model=ChannelCheckResponse)
async def is_user_in_channel( request : UserCheck) -> bool:
    try:
        channel_id = -1002553412697
        user_id = request.user_id
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        # Проверяем статус пользователя
        if member.status in ['member', 'administrator', 'creator']:
            return ChannelCheckResponse(
                is_member=True
            )
        elif member.status in ['left', 'kicked']:
            return ChannelCheckResponse(
                is_member=False
            )
        else:
            return ChannelCheckResponse(
                is_member=False
            )
    except TelegramBadRequest as e:
        # Пользователь не найден в канале
        if "user not found" in str(e).lower():
            return ChannelCheckResponse(
                is_member=False
            )
        # Другие ошибки
        logging.WARNING(f"Ошибка при проверке: {e}")
        return ChannelCheckResponse(
                is_member=False
            )







# Комманда Рассылки 
@dp.message(Command("sendall"))
async def sendmessagestoall(message: Message,state: FSMContext):
    if message.from_user.id in Admins:
        await message.answer(f'Здравсвтуйте <b>{message.from_user.first_name}</b> . Хотите ли вы разослать сообщение с фоткой?',parse_mode="HTML",reply_markup=photoyesorno)
    else:
        await message.answer("Error!")

@dp.callback_query(lambda c: c.data in ["yesphoto", "nophoto"])
async def process_photo_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yesphoto":
        await callback.message.answer("Отправьте фотку")
        await state.set_state(Sendall.GET_PHOTO)
    else:
        await callback.message.answer("Теперь отправьте основной текст!")
        await state.set_state(Sendall.GET_TEXT)

@dp.message(Sendall.GET_PHOTO , F.photo)
async def get_photo2(message: Message, state : FSMContext):
    await state.update_data(GET_PHOTO=message.photo[-1].file_id)
    await message.answer("Теперь отправьте основной текст!")
    await state.set_state(Sendall.GET_TEXT)

@dp.message(Sendall.GET_TEXT)
async def gettext123(message: Message, state: FSMContext):
    await state.update_data(GET_TEXT=message.text)
    await message.answer("Продолжить с кнопкой или нет ? ",reply_markup=buttonsyesorno)

# Обработка выбора с кнопкой или без
@dp.callback_query(lambda c: c.data in ["yesbutton", "nobutton"])
async def process_button_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "yesbutton":
        await callback.message.answer("Отправьте текст кнопки!")
        await state.set_state(Sendall.GET_BUTTON)
    else:
        await send_preview(callback.message, state)

# Предпросмотр сообщения
async def send_preview(message, state: FSMContext):
    data = await state.get_data()
    if 'GET_PHOTO' in data and data['GET_PHOTO']:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=data['GET_PHOTO'],
            caption=data['GET_TEXT'],
            reply_markup=create_keyboard(data)
        )
        await state.set_state(Sendall.CONFIRM)
    else:
        await message.answer(
            text=data['GET_TEXT'],
            reply_markup=create_keyboard(data)
        )
        await state.set_state(Sendall.CONFIRM)
    await message.answer("Чтобы начать отправку отправьте \n<b>да</b>\nЕсли хотите отменить то \n<b><i>нет</i></b>",parse_mode="HTML")

@dp.message(Sendall.GET_BUTTON)
async def getbutton123(message: Message, state: FSMContext):
    await state.update_data(GET_BUTTON=message.text)
    await message.answer("Теперь отправьте ссылку, которую кнопка будет содержать:")
    await state.set_state(Sendall.GET_LINK)

@dp.message(Sendall.GET_LINK)
async def getlink342(message: Message, state: FSMContext):
    await state.update_data(GET_LINK=message.text)
    await send_preview(message, state)
    





# Создание клавиатуры
def create_keyboard(data):
    if 'GET_BUTTON' in data and data['GET_BUTTON'] and 'GET_LINK' in data and data['GET_LINK']:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=data['GET_BUTTON'], url=data['GET_LINK'])]
            ]
        )
    

    return None


# Подтверждение рассылки
@dp.message(Sendall.CONFIRM)
async def getconfirmation(message: Message, state: FSMContext):
    logging.info(f"Confirm_send вызван пользователем {message.from_user.username}")
    print(f"Confirm_send вызван пользователем {message.from_user.username}")
    text = message.text.lower()
    if text in ["да", "yes", "ок", "го", "let's go"]:
        await state.update_data(CONFIRM=True)
        await message.answer("Начинаю рассылку!")
        logging.info(f"confirm_send вызван пользователем {message.from_user.username}")
        print(f"confirm_send вызван пользователем {message.from_user.username}")
        data = await state.get_data()
        added_keyboards = create_keyboard(data)
        sent_users = set()
        user_ids = list(set(await get_all_users()))  # уникальность заранее
        j = 0
        for i in user_ids:
            try:
                if i in sent_users:
                    continue
                elif 'GET_PHOTO' in data and data['GET_PHOTO']:
                    await bot.send_photo(
                        chat_id=i,
                        photo=data['GET_PHOTO'],
                        caption=data['GET_TEXT'],
                        reply_markup=added_keyboards
                    )
                    sent_users.add(i)
                else:
                    await bot.send_message(
                        chat_id=i,
                        text=data['GET_TEXT'],
                        reply_markup=added_keyboards
                    )
                    sent_users.add(i)
                j += 1
            except TelegramForbiddenError:
                logging.warning(f"Пользователь {i} заблокировал бота.")
            except Exception as e:
                logging.warning(f"Произошла ошибка при отправке сообщения пользователю {i}: {e}")
            finally:
                await asyncio.sleep(0.50)  # Добавляем задержку между сообщениями
        await message.answer(f"Количество успешно отправленных рассылок: {j}")
        await message.answer(f"Пользователи в SET {sent_users}")
        with open("data.txt", "w") as file:
            for user in sent_users:
                file.write(f"{user}\n")  # записывает построчно
        await state.clear()
    else:
        logging.info(f"notconfirming вызван пользователем {message.from_user.username}")
        await message.answer("Вы отменили рассылку!")
        await state.clear()
        return

################################################    





@dp.message(Command("newinfo"))
async def newsendall(message: Message):
    username = message.from_user.username
    CONFIRM = False
    logging.warning(f"Пользователь {username} вызвал /newinfo")
    message_text = """Привет всем участникам челленджа!
<b>Чтобы мы смогли выбрать победителей, убедитесь что у вас аккаунт в инстаграм открытый и в актуальных есть все выполненные задания.</b>
Пожалуйста подтвердите свое участие в челлендже и выполнении условий.
<b>‼️Нажмите да если выполнили все задания, и у вас открытый аккаунт в инстаграм. ‼️</b>
"""
    if CONFIRM==True:
        return
    await message.answer(message_text, parse_mode="HTML", reply_markup=buttons.participating)
    CONFIRM = True
    user_ids = list(set(await get_all_users()))  # уникальность заранее
    sent_users = set()
    j = 0
    for i in user_ids:
        try:
            if i in sent_users:
                continue
            else:
                await bot.send_message(
                    chat_id=i,
                    text=message_text,
                    reply_markup=buttons.participating
                )
                sent_users.add(i)
            j += 1
        except TelegramForbiddenError:
            logging.warning(f"Пользователь {i} заблокировал бота.")
        except Exception as e:
            logging.warning(f"Произошла ошибка при отправке сообщения пользователю {i}: {e}")
        finally:
            await asyncio.sleep(0.50)  # Добавляем задержку между сообщениям
    await message.answer(f"Количество успешно отправленных рассылок: {j}")
    await message.answer(f"Пользователи в SET {len(sent_users)}")
    
    


@dp.callback_query(lambda callback_query: callback_query.data in ["yes_i_am", "no_im_not"])
async def get_answer_from_participate(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data == "yes_i_am":
        await callback.message.answer("Спасибо за ответ!")
        async with aiosqlite.connect('users.db') as db:
            answer = "Да"
            await db.execute('''
                UPDATE challenges
                SET answer_status = ?
                WHERE user_id = ?
            ''', (answer, user_id))
            await db.commit()
            try:
                await callback.message.delete()
            except Exception as e:
                logging.warning(f"Не удалось удалить сообщение: {e}")

            
    else:
        await callback.message.answer("Спасибо за ответ!")
    























async def senddbfile():
    document = FSInputFile(r"../ON STUDY WEBHOOK/users.db")
    await bot.send_document(bdgroupid,document,message_thread_id=1)


# Отправка базы данных если что-то нужно будет
@router.message(F.text.lower() == "бд")
async def getdbofbot(message: Message):
    usid = message.from_user.id
    if message.from_user.id not in Admins:
        await message.answer("Доступ запрещен!")
    else:
        document = FSInputFile(r"../ON STUDY WEBHOOK/users.db")
        # await bot.send_document(bdgroupid,document)
        await bot.send_document(usid,document)

# Записаться на консультацию   
@router.callback_query(lambda callback_query: callback_query.data == "consult")
async def consultfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f"""Привет <b>{callback.from_user.username}</b>

Отправь пожалуйста нам некоторые данные чтобы мы связались с тобой.

<b>Номер телефона</b>   : <i><u>Пример</u> - 0770290211</i>
<b>Твое настоящее имя</b>   : <i><u>Пример</u> - Акылай</i>
<b>Насчет чего хотел(а) бы проконсультироваться ? </b>

<i><u>Пример 1</u> - Я бы хотел(а) узнать про процесс поступления</i>
                                  
<i><u>Пример 1</u> - Я хочу узнать про курсы SAT/IELTS</i>

<i><u>Пример 1</u> - Какие достижения|статы нужны для поступления на грант ? </i>
                                  
<i><b>Пожалуйста подождите немного , наш менеджер ответит вам как только освободится 🙏</b></i>
""",parse_mode="HTML")
    await state.set_state(consult.main)


# Вся ИНФА
@router.message(consult.main)
async def get_info(message: Message, state: FSMContext):
    main=message.text
    await bot.send_message(bdgroupid,f"""@{message.from_user.username} хочет на консультацию\n\n
<code>{main}</code>
""",message_thread_id=6,parse_mode="HTML")
    await state.clear() # очищаем стейт


async def setup():
    
    
    # Регистрация роутеров
    dp.include_router(callbackrouter)
    dp.include_router(router)
    dp.include_router(startrouter)
    dp.include_router(pay_router)

    
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Bishkek"))
    trigger_1 = CronTrigger(hour=22, minute=48, day_of_week="0-6", timezone="Asia/Bishkek")
    scheduler.add_job(senddbfile, trigger_1)
    # Запускаем планировщик в фоновом режиме
    scheduler.start()







# События FastAPI
@app.on_event("startup")
async def on_startup():
    # Устанавливаем вебхук
    webhook_info = await bot.set_webhook(
        url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        drop_pending_updates=True
    )
    logging.info(f"Webhook установлен: {webhook_info}")
    
    # Ваш текущий код
    await setup()
    logging.info("Сервер запущен 🚀")
    
    
    



# Запуск FastAPI через Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

