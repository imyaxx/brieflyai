from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def subscription_keyboard(author_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Unsubscribe",
                    callback_data=f"unsubscribe:{author_username}",
                )
            ]
        ]
    )
