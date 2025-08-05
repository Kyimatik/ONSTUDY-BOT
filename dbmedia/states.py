from aiogram.fsm.state import StatesGroup , State
#Получение данных 
class NewAppointment(StatesGroup):
    title = State()
    date = State()
    time = State()
    slots = State()



class consult(StatesGroup):
    main = State()

class TitleApp(StatesGroup):
    ID = State()
    data = State()

class DateApp(StatesGroup):
    ID = State()
    data = State()

class TimeApp(StatesGroup):
    ID = State()
    data = State()

class SlotApp(StatesGroup):
    ID = State()
    data = State()


class Question(StatesGroup):
    main = State()

