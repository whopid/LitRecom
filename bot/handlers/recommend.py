from aiogram import Router, types
from aiogram.filters import Command

from app.infrastructure.requests import get_recommendations
from bot.keyboards.inline import feedback_keyboard


router = Router()

@router.message(Command("recommend"))
async def recommend(message: types.Message):
    recommendation = get_recommendations(message.from_user.id)[0] # TODO: откуда взять amount?
    await message.answer(
        f"📖 {recommendation['title']}",
        reply_markup=feedback_keyboard(recommendation["google_id"]),
    )

