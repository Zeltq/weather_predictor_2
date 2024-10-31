'''
Файл, в котором полностью прописана логика телеграм бота.
'''

import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from config import TOKEN, api_key
from functs import split_cities, get_weather_description_by_cities
 

class Period(StatesGroup):
    """Класс содержит состояние пользователей.
    Это нужно для того, чтобы бот запоминал, на сколько дней пользователю нужно выдавать прогноз"""
    period_3 = State()
    period_5 = State()


# Это объект клавиатуры, для того чтобы пользователь мог выбрать, на сколько дней ему показывать прогноз
periods = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='3 дня', callback_data='3days')], [InlineKeyboardButton(text='5 дней', callback_data='5days')]])


bot = Bot(token=TOKEN)
dp = Dispatcher()



# Обработка комманд вид /command
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Period.period_3)
    await message.answer('Привет, я бот, который предоставляет погоду по вашему списку городов. \n\nЧтобы начать, введите команду /period, после чего выберите, на какой период выводить прогноз (По умолчанию - это 3 дня). Далее введите список городов, разделённых запятой и пробелом (например: Москва, Сочи, Мурманск), после чего пришлёт вам описание погоды по заданным параметрам.')

@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Чтобы начать, введите команду /period, после чего выберите, на какой период выводить прогноз. Далее введите список городов, разделённых запятой и пробелом (например: Москва, Сочи, Мурманск), после чего пришлёт вам описание погоды по заданным параметрам.')

@dp.message(Command('period'))
async def cmd_period(message: Message):
    await message.answer('Выберите, на какой период показывать погоду', reply_markup=periods)


# Обработка запроса на изменение периода отображения погоды
@dp.callback_query()
async def change_period(callback: CallbackQuery, state: FSMContext):
    if callback.data == '3days':
        await state.set_state(Period.period_3)
        await callback.answer('Успешно')
        await callback.message.answer('Теперь вы будете получать данные о погоде на 3 дня вперёд')
    elif callback.data == '5days':
        await state.set_state(Period.period_5)
        await callback.answer('Успешно')
        await callback.message.answer('Теперь вы будете получать данные о погоде на 5 дней вперёд')
    else:
        await callback.message.answer('Ошибка: Не удалось обработать запрос на изменение периода получения данных о погоде.')

# Обработка введённого текста (набор городов)
@dp.message(Period.period_3)
async def weather_3_days(message: Message):
    cities = await split_cities(text=message.text)

    answer = await get_weather_description_by_cities(cities=cities, api_key=api_key, days=3)

    if type(answer) is Exception: #тут мы проверяем, если нам пришла ошибка и пишем пользователю о неё
        await message.answer(str(answer))
    else:
        for key in answer:
            await message.answer(answer[key])

@dp.message(Period.period_5)
async def weather_5_days(message: Message):
    cities = await split_cities(text=message.text)

    answer = await get_weather_description_by_cities(cities=cities, api_key=api_key, days=5)

    if type(answer) is Exception: #тут мы проверяем, если нам пришла ошибка и пишем пользователю о неё
        await message.answer(str(answer))
    else:
        for key in answer:
            await message.answer(answer[key])

@dp.message(F.text)
async def weather_any_days(message: Message):
    cities = await split_cities(text=message.text)

    answer = await get_weather_description_by_cities(cities=cities, api_key=api_key, days=3)

    if type(answer) is Exception: #тут мы проверяем, если нам пришла ошибка и пишем пользователю о неё
        await message.answer(str(answer))
    else:
        for key in answer:
            await message.answer(answer[key])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")