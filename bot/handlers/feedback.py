from aiogram import Router, types, F
from sqlmodel import Session, select

from app.infrastructure.requests import post_feedback


router = Router()

@router.callback_query(F.data.startswith("like") | F.data.startswith("dislike"))
async def feedback(callback: types.CallbackQuery):
    action, google_id = callback.data.split(":")
    post_feedback(action, google_id, callback.from_user.id)
    await callback.answer("Сохранено ❤️")
