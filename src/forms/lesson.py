from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from src.telegram_api import MESSAGES, KEYBOARDS, dp, db, States
from src.utils import list_to_table
from datetime import datetime


class LessonStates(StatesGroup):
    delete = State()
    date = State()
    topics = State()
    diff = State()


async def get_lessons(message: Message, state: FSMContext):
    lessons = await db.get_lessons(message.from_user.id)
    lessons_str = f'``` Записанные уроки:\n{list_to_table(lessons, ["Дата", "Темы", "Сложность"])}\n```'
    await message.reply(lessons_str, reply=False, reply_markup=KEYBOARDS["main"], parse_mode="markdown")
    await state.set_state(States.main)


@dp.message_handler(state=States.lessons)
async def process_action(message: Message, state: FSMContext):
    await state.finish()
    await LessonStates.date.set()
    if message.text == "Добавить":
        pass
    elif message.text == "Удалить":
        await state.set_state(LessonStates.delete)
        await message.reply("Вы действительно хотите удалить все уроки? (да/нет)", reply_markup=KEYBOARDS["yes_no"])
        return
    elif message.text == "Получить":
        await get_lessons(message, state)
        return

    async with state.proxy() as data:
        data["user_id"] = message.from_user.id
    await message.reply("Введите дату в формате: дд.мм.гггг", reply=False, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=LessonStates.delete)
async def delete_material(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        await db.delete_lessons(message.from_user.id)
        await state.finish()
        await States.main.set()
        await message.reply("Все уроки удалены", reply_markup=KEYBOARDS["main"])
    else:
        state.finish()
        await States.lessons.set()
        await message.reply("Отмена", reply_markup=KEYBOARDS["sub"])


@dp.message_handler(state=LessonStates.date)
async def process_date(message: Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            date = datetime.strptime(message.text, "%d.%m.%Y").date()
        except:
            await message.reply("Неверный формат даты, попробуйте еще")
        data["lesson_date"] = date

    await state.set_state(LessonStates.topics)
    await message.reply("Введите темы урока", reply=False)


@dp.message_handler(state=LessonStates.topics)
async def process_word(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["topics"] = message.text

    await state.set_state(LessonStates.diff)
    await message.reply("Оцените сложность урока", reply=False)


@dp.message_handler(lambda msg: msg.text.isnumeric(), state=LessonStates.diff)
async def process_diff(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["difficulty"] = int(message.text)

        await message.reply(f"Урок добавлен", reply_markup=KEYBOARDS["main"])

        await db.insert_lesson(**data)

    await state.finish()
    await States.main.set()
