from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.main_keyboard import main_keyboard
from bot.states.questionnaire_state import QuestionnaireState
from infrastructure.db import get_session
from infrastructure.requests import get_genre_by_name, create_genre, get_user_by_telegram_id, create_preference

router = Router()


@router.callback_query(
    QuestionnaireState.waiting_for_genres
)
async def save_genre(callback: types.CallbackQuery, state: FSMContext):

    genre_name = callback.data.split("_")[1]
    genre_name_ru = callback.data.split("_")[0]
    data = await state.get_data()
    selected_genres = data.get("selected_genres", [])

    if genre_name in selected_genres:
        await callback.answer(
            "Ты уже выбрал(-а) этот жанр 🙂",
            show_alert=True
        )
        return

    selected_genres.append(genre_name)

    await state.update_data(selected_genres=selected_genres)

    remaining = 3 - len(selected_genres)

    if len(selected_genres) < 3:
        await callback.answer()

        await callback.message.answer(
            f"Жанр '{genre_name_ru}' добавлен ✅\n"
            f"Осталось выбрать: {remaining}"
        )

        return

    async for session in get_session():
        user = await get_user_by_telegram_id(callback.from_user.id, session)

        for genre_name in selected_genres:
            genre = await get_genre_by_name(genre_name, session)
            if not genre:
                genre = await create_genre(genre_name, session)

            await create_preference(user_id=user.id, genre_id=genre.id)

    await callback.message.answer(
        "Анкета завершена ✅"
    )

    await callback.message.answer(
        f"Твои жанры:\n{', '.join(selected_genres)}"
    )

    await callback.message.answer(
        "Теперь можешь пользоваться ботом 📚",
        reply_markup=main_keyboard
    )

    await state.clear()

    await callback.answer()
