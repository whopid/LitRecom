from aiogram.fsm.state import StatesGroup, State


class QuestionnaireState(StatesGroup):
    waiting_for_genres = State()
