from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from src.telegram_api import MESSAGES, KEYBOARDS, dp, db, States
from src.utils import list_to_table


class MaterailStates(StatesGroup):
    delete = State()
    name = State()
    link = State()
    mark = State()


async def get_materials(message: Message, state: FSMContext):
    materials = await db.get_materials(message.from_user.id)
    materials_str = f"``` Записанные материалы:\n{list_to_table(materials, ['Название', 'Ссылка', 'Оценка'])} ```"
    await message.reply(materials_str, reply=False, reply_markup=KEYBOARDS["main"], parse_mode='markdown')
    await state.set_state(States.main)


@dp.message_handler(state=States.materials)
async def process_action(message: Message, state: FSMContext):
    await state.finish()
    await MaterailStates.name.set()
    if message.text == "Добавить":
        pass
    elif message.text == "Удалить":
        await state.set_state(MaterailStates.delete)
        await message.reply("Вы действительно хотите удалить все материалы? (да/нет)", reply_markup=KEYBOARDS["yes_no"])
        return
    elif message.text == "Получить":
        await get_materials(message, state)
        return

    async with state.proxy() as data:
        data["user_id"] = message.from_user.id
    await message.reply("Введите название материала", reply=False, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=MaterailStates.delete)
async def delete_material(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        await db.delete_materials(message.from_user.id)
        await state.finish()
        await States.main.set()
        await message.reply("Все материалы удалены", reply_markup=KEYBOARDS["main"])
    else:
        state.finish()
        await States.materials.set()
        await message.reply("Отмена", reply_markup=KEYBOARDS["sub"])


@dp.message_handler(state=MaterailStates.name)
async def process_date(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await state.set_state(MaterailStates.link)
    await message.reply("Введите ссылку на материал", reply=False)


@dp.message_handler(state=MaterailStates.link)
async def process_word(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["link"] = message.text

    await state.set_state(MaterailStates.mark)
    await message.reply("Оцените материал", reply=False)


@dp.message_handler(lambda msg: msg.text.isnumeric(), state=MaterailStates.mark)
async def process_diff(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["mark"] = int(message.text)

        await message.reply(f"Материал добавлен", reply_markup=KEYBOARDS["main"])

        await db.insert_material(**data)

    await state.finish()
    await States.main.set()
