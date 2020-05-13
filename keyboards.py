from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


start = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
start.insert(KeyboardButton('🤖О чат ботах'))
start.insert(KeyboardButton('📂Готовые кейсы'))
start.insert(KeyboardButton('🛒Заказать чат-бота'))
start.insert(KeyboardButton('📲Контакты'))
start.insert(KeyboardButton('🤝Партнерство'))
start.insert(KeyboardButton('⚙️Где используют чат ботов?'))
start.add(KeyboardButton('❓Получить консультацию'))

capabilities = InlineKeyboardMarkup(row_width=3)
capabilities.add(InlineKeyboardButton('💪🏻 Возможности чат-бота', callback_data='capabilities'))


info = InlineKeyboardMarkup(row_width=3)
pay = InlineKeyboardButton('🛒Заказать чат-бота', callback_data='pay')
info.insert(pay)
info.insert(InlineKeyboardButton('❔Задать вопрос', callback_data='question'))


left = InlineKeyboardButton('⬅️', callback_data='left')
right = InlineKeyboardButton('➡️', callback_data='right')


connection = InlineKeyboardMarkup(row_width=2)
connection.insert(InlineKeyboardButton('Написать', url='https://t.me/Zantrius'))
connection.insert(InlineKeyboardButton('Instagram', url='https://www.instagram.com/khnychenko_vladislav/'))


async def cart_keyboard(lenght, i, items):
    items_kb = InlineKeyboardMarkup(row_width=3)
    if lenght != 1:
        items_kb.row(left, InlineKeyboardButton(text=f'{i + 1} / {lenght}', callback_data='None'), right)
    if items.url:
        items_kb.add(InlineKeyboardButton(text='🤖Перейти в бота', url=items.url))
    if items.video_url:
        items_kb.add(InlineKeyboardButton(text='💻Видео демонстрация работы ', url=items.video_url))
    items_kb.add(pay)
    #items_kb.add(InlineKeyboardButton(text='Хочу  ', callback_data='more'))
    return items_kb


