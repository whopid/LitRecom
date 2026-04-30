from aiogram import Router, types
from aiogram.filters import Command

from infrastructure.db import get_session
from infrastructure.requests import (
    get_user_by_telegram_id,
    get_recommendations
)
from bot.keyboards.feedback_keyboard import feedback_keyboard

router = Router()


@router.message(Command("recommend"))
async def recommend_command(message: types.Message):
    await send_recommendation(message)

@router.message(lambda message: message.text == "📚 Получить рекомендацию")
async def recommend_button(message: types.Message):
    await send_recommendation(message)


async def send_recommendation(message: types.Message):
    async for session in get_session():

        user = await get_user_by_telegram_id(
            message.from_user.id,
            session
        )

        if not user:
            await message.answer(
                "Сначала пройди анкету через /start 📚"
            )
            return

        recommendations = await get_recommendations(
            user_id=user.id,
            session=session,
            amount=1
        )

        if not recommendations:
            await message.answer(
                "Пока не удалось найти рекомендации 😢"
            )
            return

        recommendation = recommendations[0]

        photo_url = recommendation.get("thumbnail")

        caption = (
            f"📖 {recommendation['title']}\n\n"
            f"{recommendation.get('description', 'Описание отсутствует')}"
        )

        if photo_url:

            await message.answer_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=feedback_keyboard(recommendation["google_book_id"])
            )

        else:

            await message.answer(
                caption,
                reply_markup=feedback_keyboard(recommendation["google_book_id"])
            )
