from aiogram.fsm.state import StatesGroup, State


class UsernameState(StatesGroup):
    waiting_for_username = State()
