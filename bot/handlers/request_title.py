from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from bot.states.search_state import SearchState


router = Router()

@router.message(lambda message: message.text == "🔍 Поиск")
async def start_search(message: types.Message, state: FSMContext):

    await message.answer(
        "Напишите название книги, которую Вы ищете."
    )

    await state.set_state(SearchState.waiting_for_query)
