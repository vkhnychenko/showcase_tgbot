from aiogram.dispatcher.filters.state import StatesGroup, State


class Consultation(StatesGroup):
    business_type = State()


