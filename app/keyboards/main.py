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


from urllib.parse import quote
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def referral_share_keyboard(ref_link: str) -> InlineKeyboardMarkup:
    share_message = (
        "Միացի՛ր Domus-ի Telegram ալիքին 🎁\n"
        "Հրավիրի՛ր ընկերներ և միացի՛ր արշավին։\n"
        "Ակտիվ մասնակիցներից 1 օգտատեր կընտրվի պատահական սկզբունքով և կստանա նվեր։\n\n"
        f"{ref_link}"
    )

    encoded_message = quote(share_message)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Կիսվել ընկերների հետ",
                    url=f"https://t.me/share/url?url={encoded_message}",
                )
            ]
        ]
    )