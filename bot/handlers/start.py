from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlmodel import Session, select

from app.infrastructure.db import engine
from app.infrastructure.models import User


router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    with Session(engine) as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = session.exec(stmt).first()

        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
            )
            session.add(user)
            session.commit()

    await message.answer("Привет! Я бот-рекомендатор книг 📚")
