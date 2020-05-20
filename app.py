from settings import BOT_TOKEN, PROXY_URL, PROXY_LOGIN, PROXY_PASS, ADMIN_ID
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import CallbackQuery
import logging
import keyboards as kb
import aiohttp
from database import DBCommands, create_db
from message_text import bot_info, bot_info_more, bot_quote, usage
from states import Consultation

db = DBCommands()

logging.basicConfig(level=logging.INFO)

PROXY_AUTH = aiohttp.BasicAuth(login=PROXY_LOGIN, password=PROXY_PASS)

bot = Bot(token=BOT_TOKEN,
          #proxy=PROXY_URL,
          #proxy_auth=PROXY_AUTH,
          parse_mode="HTML")

dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(dp):
    await create_db()


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    referral = message.get_args()
    await db.add_new_user(referral=referral)
    text = f'Привет, {message.from_user.full_name}!\n\n' \
           f'Наша команда занимается разработкой чат-ботов для бизнеса.' \
           f'Здесь ты можешь посмотреть готовые кейсы и задать интересующие вопросы.\n' \
           f'Вот некоторые возможности которые могут чат-боты:\n\n' \
           f'🎯собирать в одну базу вашу аудиторию,\n' \
           f'🎯автоматизировать бизнес-процессы,\n' \
           f'🎯экономить время и бюджет,\n' \
           f'🎯приводить новых клиентов и повторно возвращать старых,\n' \
           f'🎯быть на связи с клиентами 24/7.\n\n' \
           f'Выбирай нужный раздел и изучай 🔎'
    await message.answer(text=text, reply_markup=kb.start)


@dp.message_handler(text='🤖О чат ботах', state='*')
async def books_handler(message: types.Message):
    await message.answer(bot_info, reply_markup=kb.capabilities)


@dp.callback_query_handler(lambda call: call.data in ['capabilities'], state='*')
async def items_handler(call: CallbackQuery):
    await call.message.answer(bot_info_more)
    await call.message.answer(bot_quote, reply_markup=kb.info)


@dp.message_handler(text='⚙️Где используют чат ботов?',  state='*')
async def books_handler(message: types.Message):
    await message.answer(usage)


@dp.message_handler(text='🛒Заказать чат-бота', state='*')
async def books_handler(message: types.Message):
    await message.answer('Для заказа напишите бизнес которым вы занимаетесь.')
    await Consultation.business_type.set()


@dp.message_handler(text='📲Контакты', state='*')
async def books_handler(message: types.Message):
    print(message)
    await message.answer('Можете связаться по доступным ссылкам', reply_markup=kb.connection)


@dp.message_handler(text='🤝Партнерство', state='*')
async def books_handler(message: types.Message):
    bot_username = (await bot.me).username
    bot_link = f'http://t.me/{bot_username}?start={message.from_user.id}'
    count_referrals = await db.count_referrals()
    await message.answer(f'<b>Партнерская программа</b>\n\n'
                         f'Получи 500 рублей за каждого, кто закажет разработку бота!\n\n'
                         f'Ссылка для приглашения:\n'
                         f'{bot_link} \n\n'
                         f'Всего рефералов: {count_referrals}')


@dp.message_handler(text='📂Готовые кейсы', state='*')
async def books_handler(message: types.Message, state: FSMContext):
    await message.answer('Здесь вы можете посмотреть тестовые версии ботов.')
    items = await db.get_items()
    print(items)
    items_kb = await kb.cart_keyboard(len(items), 0, items[0])
    await message.answer(f'<b>{items[0].name}</b>\n'
                         f'<a href="{items[0].photo_url}">..</a>\n'
                         f'{items[0].description}', reply_markup=items_kb)
    await state.update_data(items=items, i=0)


@dp.callback_query_handler(lambda call: call.data in ['pay', 'question'], state='*')
async def items_handler(call: CallbackQuery):
    await bot.answer_callback_query(call.id)
    if call.data == 'pay':
        await call.message.answer('Каким бизнесом вы занимаетесь?Сообщение пишите прямо сюда')
        await Consultation.business_type.set()
    if call.data == 'question':
        await call.message.answer('Напишите какой у вас вопрос?')
        await Consultation.business_type.set()


@dp.message_handler(text='❓Получить консультацию', state='*')
async def books_handler(message: types.Message):
    await message.answer('Для какой сферы вам потребуется бот?Сообщение пишите прямо сюда')
    await Consultation.business_type.set()


@dp.message_handler(state=Consultation.business_type)
async def books_handler(message: types.Message, state: FSMContext):
    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.answer('Отлично!Скоро с вами свяжемся.')
    await state.reset_state()


@dp.callback_query_handler(lambda call: call.data in ['left', 'right'], state='*')
async def items_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('items')
    if call.data == 'right':
        await bot.answer_callback_query(call.id)
        i = data.get('i')
        if i != len(items) - 1:
            i = i + 1
            items_kb = await kb.cart_keyboard(len(items), i, items[i])
            await call.message.edit_text(
                f'<b>{items[i].name}</b>\n'
                f'<a href="{items[i].photo_url}">..</a>\n'
                f'{items[i].description}', reply_markup=items_kb
            )
            await state.update_data(i=i)

    if call.data == 'left':
        await bot.answer_callback_query(call.id)
        i = data.get('i')
        if i != 0:
            i = i-1
            items_kb = await kb.cart_keyboard(len(items), i, items[i])
            await call.message.edit_text(
                f'<b>{items[i].name}</b>\n'
                f'<a href="{items[i].photo_url}">..</a>\n'
                f'{items[i].description}', reply_markup=items_kb
            )
            await state.update_data(i=i)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)




