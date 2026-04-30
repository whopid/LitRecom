from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

genre_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Фантастика", callback_data="Фантастика_Science Fiction")
        ],
        [
            InlineKeyboardButton(text="Детектив", callback_data="Детектив_Detective")
        ],
        [
            InlineKeyboardButton(text="Психология", callback_data="Психология_Psychology")
        ],
        [
            InlineKeyboardButton(text="Романтика", callback_data="Романтика_Romance")
        ],
        [
            InlineKeyboardButton(text="История", callback_data="История_History")
        ]
    ]
)
