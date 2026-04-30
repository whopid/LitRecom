from aiogram import Router, types

from bot.keyboards.main_keyboard import main_keyboard
from infrastructure.db import get_session
from infrastructure.requests import get_user_by_telegram_id, delete_feedbacks_and_preferences


router = Router()

@router.callback_query(lambda c: c.data == "reset_preferences")
async def reset_feedbacks(callback: types.CallbackQuery):
    async for session in get_session():
        user = await get_user_by_telegram_id(callback.from_user.id, session)
        await delete_feedbacks_and_preferences(user.id, session)

        await callback.message.answer(
            f"{user.username}, Ваши оценки и предпочтения сброшены. "
            f"Установите новые предпочтения с помощью /start",
            reply_markup=main_keyboard
        )
        await callback.answer()
