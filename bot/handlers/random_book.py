import random

from aiogram import Router, types

from services.google_books_api import (
    get_random_book_by_genre,
)
from bot.keyboards.feedback_keyboard import feedback_keyboard

router = Router()

genres = [  # это плохо
        "fantasy",
        "science fiction",
        "detective",
        "romance",
        "history",
        "philosophy",
        "psychology",
        "thriller",
        "adventure",
        "horror",
    ]

@router.message(lambda message: message.text == "🎲 Случайная книга")
async def random_book(message: types.Message):
    genre = random.choice(genres)
    book = await get_random_book_by_genre(genre)

    if not book:
        await message.answer(
            "Не удалось найти случайную книгу 😢"
        )
        return

    photo_url = book.get("thumbnail")

    caption = (
        f"🎲 Случайная книга\n\n"
        f"📖 {book['title']}\n\n"
        f"{book.get('description', 'Описание отсутствует')}"
    )

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
