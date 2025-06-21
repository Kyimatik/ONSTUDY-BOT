from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os 

load_dotenv("onstudy.env")

TOKEN = os.getenv("Token")

bot = Bot(TOKEN)
dp = Dispatcher()