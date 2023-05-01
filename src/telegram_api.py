from aiogram import Bot, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup, Message, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from src.db import Database
from src.config import Config

MESSAGES = {
    "start": """Добро пожаловать в телеграмм бот, который поможет тебе выучить иностранный язык, здесь ты можешь:
    1. Добавлять и просматривать слова и их перводы
    2. Добавлять и просматривать полезные материалы и ссылки на них
    3. Добавлять и просматривать записи об уроках""",
    "choose": "Выберите что сделать",
    "err": "Пожалуйста, используйте клавиуатуру"
}


class States(StatesGroup):
    main = State()
    words = State()
    lessons = State()
    materials = State()


bot = Bot(token=Config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database(Config.DB_PATH)

KEYBOARDS = {"main": ReplyKeyboardMarkup(),
             "sub": ReplyKeyboardMarkup(),
             "yes_no": ReplyKeyboardMarkup()}
KEYBOARDS["main"].add(KeyboardButton("Слова"))
KEYBOARDS["main"].add(KeyboardButton("Уроки"))
KEYBOARDS["main"].add(KeyboardButton("Материалы"))
KEYBOARDS["sub"].add(KeyboardButton("Добавить"))
KEYBOARDS["sub"].add(KeyboardButton("Получить"))
KEYBOARDS["sub"].add(KeyboardButton("Удалить"))
KEYBOARDS["yes_no"].add(KeyboardButton("Да"))
KEYBOARDS["yes_no"].add(KeyboardButton("Нет"))


@dp.message_handler(commands=['start', 'help'], state="*")
async def start_handler(message: Message):
    await message.reply(MESSAGES["start"], reply_markup=KEYBOARDS["main"], reply=False)
    await States.main.set()

@dp.message_handler(state=States.main)
async def main_handler(message: Message, state: FSMContext):
    state = dp.current_state(user=message.from_user.id)
    if message.text == "Слова":
        await state.set_state(States.words)
    elif message.text == "Уроки":
        await state.set_state(States.lessons)
    elif message.text == "Материалы":
        await state.set_state(States.materials)
    else:
        await message.reply(MESSAGES["err"])
        return
    await message.reply(MESSAGES["choose"], reply_markup=KEYBOARDS["sub"])


def start():
    executor.start(dp, db.init_tables())
    executor.start_polling(dp, skip_updates=True)
