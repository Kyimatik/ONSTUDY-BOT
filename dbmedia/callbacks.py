from aiogram import Router,types, F 
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from .database import init_db, get_all_users, add_user, get_all_challenge_users, add_challenge_user
from buttons import useridkb,mainkb,back
from .media import start_text,allstickersid,feedbackphotoids,resultsofstudents,feedbackofstudents,ourstudents,ieltsinfo,satinfo,challengeinfo
from aiogram.types import InputMediaPhoto
from .states import RegistrationForm


import buttons

from .media import allphotosid






router = Router()  # Создаем отдельный роутер


# Кнопка , Узнать свой UserId 🆔
@router.message(F.text.contains("Узнать свой UserId 🆔"))
async def getselfuserid(message: Message):
    userId = message.from_user.id
    await message.answer(f"Ваш User_ID - <code>{userId}</code>",parse_mode="HTML")



# Программы туров 
@router.callback_query(lambda callback_query: callback_query.data == "location")
async def aboutusfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_photo(
        allphotosid["location"],
        caption='<a href="https://go.2gis.com/v0aRJ">Адрес в <i><b>2GIS</b></i></a>',
        parse_mode="HTML",
        reply_markup=buttons.back
    )




# Программы туров 
@router.callback_query(lambda callback_query: callback_query.data == "backtomainkb")
async def backtomainmenu(callback: CallbackQuery, state: FSMContext):
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    await callback.message.answer(f"""Привет <b>{user_name}</b>!
{start_text["getstarted"]}""",parse_mode="HTML",reply_markup=mainkb)
    await add_user(user_id)




# Отзывы учеников callback  
@router.callback_query(lambda callback_query: callback_query.data == "feedback")
async def feedbackfunc(callback: CallbackQuery, state: FSMContext):
    media_group = [InputMediaPhoto(media=photo_id) for photo_id in feedbackphotoids]
    await callback.message.answer_media_group(media_group)
    await callback.message.answer("Отзывы наших учеников 😍😍❤️\nОстальные отзывы на нашей инсте 👇",reply_markup=buttons.onstudyinstas)


# О нас   
@router.callback_query(lambda callback_query: callback_query.data == "aboutus")
async def aboutusfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_photo(allphotosid["aboutusteamphoto"],start_text["aboutus"],parse_mode="HTML",reply_markup=buttons.aboutusallinfo)



# О нас   
@router.callback_query(lambda callback_query: callback_query.data == "ieltscourses")
async def ieltscoursesfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Что вам интересно ?",reply_markup=buttons.ieltskb)


# Цена   
@router.callback_query(lambda callback_query: callback_query.data == "price")
async def pricefunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(ieltsinfo["price"],parse_mode="HTML",reply_markup=buttons.getbackieltskb)

    
# Наши менторы    
@router.callback_query(lambda callback_query: callback_query.data == "ourmentors")
async def ourmentorsfunc(callback: CallbackQuery, state: FSMContext):
    media_group = [InputMediaPhoto(media=photo) for photo in [ieltsinfo["mahfuza"],ieltsinfo["sezim"]]]
    await callback.message.answer_media_group(media_group)
    await callback.message.answer("Наши менторы 😍",reply_markup=buttons.getbackieltskb)

# Наши менторы    
@router.callback_query(lambda callback_query: callback_query.data == "formatofclasses")
async def formatofclassesfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(ieltsinfo["formattext"],parse_mode="HTML",reply_markup=buttons.getbackieltskb)




#SAT
@router.callback_query(lambda callback_query: callback_query.data == "satcourses")
async def satcoursesfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Что вам интересно ?",reply_markup=buttons.satkb)


# Цена   
@router.callback_query(lambda callback_query: callback_query.data == "pricesat")
async def pricesatfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(satinfo["price"],parse_mode="HTML",reply_markup=buttons.getbacksatkb)

    
# Наши менторы    
@router.callback_query(lambda callback_query: callback_query.data == "ourmentorssat")
async def ourmentorssatfunc(callback: CallbackQuery, state: FSMContext):
    media_group = [InputMediaPhoto(media=photo) for photo in [satinfo["temirlan"],satinfo["doniyor"]]]
    await callback.message.answer_media_group(media_group)
    await callback.message.answer("Наши менторы 😍",reply_markup=buttons.getbacksatkb)

# Наши менторы    
@router.callback_query(lambda callback_query: callback_query.data == "formatofclassessat")
async def formatofclassessatfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(ieltsinfo["formattext"],parse_mode="HTML",reply_markup=buttons.getbacksatkb)






# Результаты наших студентов 
@router.callback_query(lambda callback_query: callback_query.data == "results")
async def resultsfunc(callback: CallbackQuery, state: FSMContext):
    media_group = [InputMediaPhoto(media=photo_id) for photo_id in resultsofstudents]
    await callback.message.answer_media_group(media_group)
    await callback.message.answer("Результаты наших учеников 🚀",reply_markup=buttons.backfromresultsetc)
    
# Фидбек от студентов  
@router.callback_query(lambda callback_query: callback_query.data == "feedbackfromstudents")
async def feedbackfromstudentsfunc(callback: CallbackQuery, state: FSMContext):
    media_group = [InputMediaPhoto(media=photo_id) for photo_id in feedbackofstudents]
    await callback.message.answer_media_group(media_group)
    await callback.message.answer("Отзывы наших учеников 🥺❤️",reply_markup=buttons.backfromresultsetc)

# Наши студенты 
@router.callback_query(lambda callback_query: callback_query.data == "ourstudents")
async def ourstudentsfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_photo(ourstudents[0],start_text["abdy"],parse_mode="HTML",reply_markup=buttons.backfromresultsetc)
    await callback.message.answer_photo(ourstudents[1],start_text["abay"],parse_mode="HTML",reply_markup=buttons.backfromresultsetc)
    
# Наши контакты  
@router.callback_query(lambda callback_query: callback_query.data == "contacts")
async def contactsfunc(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_photo(allphotosid["contacts"],start_text["contacts"],parse_mode="HTML",reply_markup=buttons.backfromresultsetc)
    
    
    










    





























