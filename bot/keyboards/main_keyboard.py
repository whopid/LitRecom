from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Получить рекомендацию")],
        [KeyboardButton(text="🎲 Случайная книга")],
        [KeyboardButton(text="🔍 Поиск")],
        [KeyboardButton(text="⚙️ Настройки")]
    ],
    resize_keyboard=True
)
