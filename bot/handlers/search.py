from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.feedback_keyboard import feedback_keyboard
from bot.states.search_state import SearchState
from services.google_books_api import search_books


router = Router()

@router.message(SearchState.waiting_for_query)
async def process_search(
    message: types.Message,
    state: FSMContext
):
    query = message.text
    books = await search_books(query, max_results=5)

    if not books:
        await message.answer(
            "Книги не найдены 😢"
        )

        await state.clear()
        return

    book = books[0]

    caption = (
        f"📖 {book['title']}\n\n"
        f"{book.get('description', 'Описание отсутствует')}"
    )

    photo_url = book.get("thumbnail")

    if photo_url:
        await message.answer_photo(
            photo=photo_url,
            caption=caption,
            reply_markup=feedback_keyboard(book["google_book_id"])
        )
    else:
        await message.answer(
            caption,
            reply_markup=feedback_keyboard(book["google_book_id"])
        )

    await state.clear()
