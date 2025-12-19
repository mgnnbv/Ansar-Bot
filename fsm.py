from aiogram.fsm.state import State, StatesGroup

from aiogram.fsm.state import StatesGroup, State

class QuestionStates(StatesGroup):
    waiting = State()

from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    name = State()
    short_description = State()
    additional_info = State()
    images = State()
