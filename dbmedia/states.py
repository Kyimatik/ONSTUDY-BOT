from aiogram.fsm.state import StatesGroup , State
#Получение данных 
class RegistrationForm(StatesGroup):
    FIO = State() # ФИО
    contacts = State()# Телефон 
    placeofstudying = State()# Школа Город 
    age = State()# Возраст 
    insta = State() # Инстаграм аккаунт 



class consult(StatesGroup):
    main = State()
