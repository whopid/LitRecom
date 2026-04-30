from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

settings_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить имя пользователя", callback_data="change_username")
        ],
        [
            InlineKeyboardButton(text="Сброс предпочтений", callback_data="reset_preferences")
        ],
    ]
)
