from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def feedback_keyboard(google_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👍", callback_data=f"like:{google_id}"
                ),
                InlineKeyboardButton(
                    text="👎", callback_data=f"dislike:{google_id}"
                ),
            ]
        ]
    )
