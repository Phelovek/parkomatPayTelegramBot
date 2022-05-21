from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenvy import load_env, read_file

load_env(read_file('.env'))

PAYMENTS_PROVIDER_TOKEN = os.environ['PAYMENTS_PROVIDER_TOKEN']
token = os.environ['token']
token1 = os.environ['token1']
TESSDATA_PREFIX = os.environ['TESSDATA_PREFIX']
bot = Bot(str(token))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

