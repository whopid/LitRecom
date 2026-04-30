from aiogram import Router, types, F

from infrastructure.db import get_session
from infrastructure.requests import (
    get_user_by_telegram_id,
    post_feedback
)
from services.google_books_api import get_book_by_id

router = Router()


@router.callback_query(
    F.data.startswith("like:") | F.data.startswith("dislike:")
)
async def feedback(callback: types.CallbackQuery):

    action, google_book_id = callback.data.split(":")

    async for session in get_session():

        user = await get_user_by_telegram_id(
            callback.from_user.id,
            session
        )

        if not user:
            await callback.answer(
                "Сначала пройди анкету через /start",
                show_alert=True
            )
            return

        book = await get_book_by_id(google_book_id)

        await post_feedback(
            user_id=user.id,
            genre_name=book['genre'],
            rating=action,
            session=session,
            google_book_id=google_book_id,
            title=book['title']
        )

    if action == "like":
        text = "Лайк сохранён ❤️"
    else:
        text = "Дизлайк сохранён 👍"

    await callback.answer(text)
