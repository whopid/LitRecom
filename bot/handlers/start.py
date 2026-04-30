from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlmodel import Session, select

from infrastructure.db import get_session
from infrastructure.requests import get_user_by_telegram_id, create_user
from bot.states.questionnaire_state import QuestionnaireState
from bot.keyboards.questionnaire_keyboard import genre_keyboard


router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):

    async for session in get_session():

        user = await get_user_by_telegram_id(message.from_user.id, session)

        if not user:
            await create_user(message.from_user.id, message.from_user.username, session)

    await message.answer(
        "Привет! Давай подберём тебе книги 📚"
    )

    await state.set_state(QuestionnaireState.waiting_for_genres)

    await state.update_data(selected_genres=[])

    await message.answer(
        "Выбери 3 любимых жанра 📚",
        reply_markup=genre_keyboard
    )
