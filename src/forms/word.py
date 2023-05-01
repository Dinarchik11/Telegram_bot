from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from src.telegram_api import MESSAGES, KEYBOARDS, dp, db, States
from src.utils import list_to_table


class WordStates(StatesGroup):
    delete = State()
    word = State()
    trans = State()


async def get_words(message: Message, state: FSMContext):
    words = await db.get_words(message.from_user.id)
    words_str = f"``` Записанные слова:\n{list_to_table(words, ['Слово', 'Перевод'])} ```"
    await message.reply(words_str, reply=False, reply_markup=KEYBOARDS["main"], parse_mode="markdown")
    await state.set_state(States.main)


@dp.message_handler(state=States.words)
async def process_action(message: Message, state: FSMContext):
    await state.finish()
    if message.text == "Добавить":
            pass
    elif message.text == "Удалить":
            await WordStates.delete.set()
            await message.reply("Вы действительно хотите удалить все слова? (да/нет)", reply_markup=KEYBOARDS["yes_no"])
            return
    elif message.text == "Получить":
            await get_words(message, state)
            return
    else:
        await message.reply(MESSAGES["err"])
        return

    await WordStates.word.set()
    async with state.proxy() as data:
        data["user_id"] = message.from_user.id
    await message.reply("Введите слово", reply=False, reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=WordStates.delete)
async def delete_words(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        await db.delete_words(message.from_user.id)
        await state.finish()
        await States.main.set()
        await message.reply("Все слова удалены", reply_markup=KEYBOARDS["main"])
    else:
        state.finish()
        await States.words.set()
        await message.reply("Отмена", reply_markup=KEYBOARDS["sub"])


@dp.message_handler(state=WordStates.word)
async def process_word(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["word"] = message.text

    await state.set_state(WordStates.trans)
    await message.reply("Введите перевод", reply=False)


@dp.message_handler(state=WordStates.trans)
async def process_trans(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["translation"] = message.text

        await message.reply(f"Слово добавлено", reply_markup=KEYBOARDS["main"])

        await db.insert_word(**data)

    await state.finish()
    await States.main.set()