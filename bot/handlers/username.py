from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.main_keyboard import main_keyboard
from bot.states.username_state import UsernameState
from infrastructure.db import get_session
from infrastructure.requests import get_user_by_telegram_id, update_existing_user


router = Router()

@router.callback_query(lambda c: c.data == "change_username")
async def change_username(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        "Скажите, как к Вам обращаться?"
    )

    await state.set_state(UsernameState.waiting_for_username)
    await callback.answer()

@router.message(UsernameState.waiting_for_username)
async def process_username(
    message: types.Message,
    state: FSMContext
):
    username = message.text
    async for session in get_session():
        user = await get_user_by_telegram_id(message.from_user.id, session)
        await update_existing_user(user.id, username, session)

        await message.answer(
            f"Хорошо, теперь я буду обращаться к Вам как {username}.",
            reply_markup=main_keyboard
        )

    await state.clear()
