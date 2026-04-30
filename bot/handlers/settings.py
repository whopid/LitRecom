from aiogram import Router, types

from bot.keyboards.settings_keyboard import settings_keyboard


router = Router()

@router.message(lambda message: message.text == "⚙️ Настройки")
async def change_settings(message: types.Message):
    await message.answer(
         "Выбери действие:",
        reply_markup=settings_keyboard
    )
