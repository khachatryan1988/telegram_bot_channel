from urllib.parse import quote

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


def referral_share_keyboard(ref_link: str) -> InlineKeyboardMarkup:
    share_text = "Միացի՛ր Domus-ի խաղարկությանը 🎁\nՄասնակցի՛ր և շահի՛ր նվերներ։"
    encoded_url = quote(ref_link, safe="")
    encoded_text = quote(share_text, safe="")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Կիսվել ընկերների հետ",
                    url=f"https://t.me/share/url?url={encoded_url}&text={encoded_text}",
                )
            ]
        ]
    )