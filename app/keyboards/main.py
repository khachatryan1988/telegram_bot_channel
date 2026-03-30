from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Մասնակցել")]],
        resize_keyboard=True,
    )


def participate_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Անցնել ալիք",
                    url=f"https://t.me/{channel_username.lstrip('@')}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Ստուգել մասնակցությունս",
                    callback_data="check_participation",
                )
            ],
        ]
    )


def winner_response_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Հաստատել արձագանքս",
                    callback_data="winner_confirm_response",
                )
            ]
        ]
    )