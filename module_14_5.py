from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import asyncio
from config import *
from keyboards import *
from crud_functions import *
import texts

bot = Bot(token=API)
# bot = Bot(token=api, proxy='socks5://188.165.192.99:36188')
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


# меню калорий
kb = InlineKeyboardMarkup(resize_keyboard=True)
button1 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
button2 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
kb.insert(button1)
kb.insert(button2)

# Стартовая клавиатура
kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
button3 = KeyboardButton(text='Информация')
button4 = KeyboardButton(text='Рассчитать')
button5 = KeyboardButton(text='Купить')
button6 = KeyboardButton(text='Регистрация')
kb2.insert(button3)
kb2.insert(button4)
kb2.insert(button5)
kb2.insert(button6)

# меню продуктов
kb3 = InlineKeyboardMarkup(resize_keyboard=True)
button31 = InlineKeyboardButton(text='Product1', callback_data="product_buying")
button32 = InlineKeyboardButton(text='Product2', callback_data="product_buying")
button33 = InlineKeyboardButton(text='Product3', callback_data="product_buying")
button34 = InlineKeyboardButton(text='Product4', callback_data="product_buying")
kb3.insert(button31)
kb3.insert(button32)
kb3.insert(button33)
kb3.insert(button34)

initiate_db()
get_all_products()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer(
        'Привет! Я бот помогающий твоему здоровью.14', reply_markup=kb2)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:',
                         reply_markup=kb)
    await start_message.age.set()


# @dp.message_handler(text='Рассчитать')
# async def main_menu(message):
#     await message.answer('Выберите опцию:')
#     await start_message.age.set()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    # data_age = await state.get_data()
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=int(message.text))
    # data_growth = await state.get_data()
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()


@dp.callback_query_handler(text='formulas')
async def infor(call):
    await call.message.answer("10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161")
    await call.answer()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    # norma_call = (10 х UserState.weight) + (6,25 х UserState.weight) – (5 х UserState.growth) + 5.
    norma_call = (10 * data['weight']) + (6.25 * data['growth']) - (5 * data['age']) + 5
    await message.answer(f'Ваша норма колорий {norma_call}')
    # Для мужчин: (10 х вес в кг) + (6,25 х рост в см) – (5 х возраст в г) + 5.
    await state.finish()


# "10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161"

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer(
        'Привет! Я бот помогающий твоему здоровью введите "Рассчитать" чтобы посчитать вашу норму колорий')


@dp.message_handler(text='Купить')
async def kupit(message: types.Message):
    await get_buying_list(message)


async def get_buying_list(message: types.Message):
    products = get_all_products()
    if not products:
        print(products)
        await message.answer("Список товаров пуст.")
        return
    response = "Список товаров:\n"
    for product in products:
        response = f"Название: {product[2]} | Описание: {product[1]} | Цена: {product[3]} руб.\n"
        await message.answer(response)
        with open(f'files1\product{product[0]}.jpg', "rb") as img:
            await message.answer_photo(img, )
    # await message.answer(response)


@dp.callback_query_handler(text="product_buying")
async def handle_product_buying(call: types.CallbackQuery):
    await send_confirm_message(call)


async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()  # Закрыть уведомление


@dp.message_handler(text='Регистрация')
async def sing_up(message: types.Message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        user_data = await state.get_data()
        add_user(user_data['username'], user_data['email'], age)
        await message.answer("Регистрация завершена! Вы успешно добавлены в базу данных.")
        await state.finish()
    except ValueError:
        await message.answer("Возраст должен быть числом. Попробуйте ещё раз:")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
