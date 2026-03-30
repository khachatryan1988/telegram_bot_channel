import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest


def _is_member(status: ChatMemberStatus) -> bool:
    return status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }


async def is_user_subscribed(
    bot: Bot, channel_username: str, tg_user_id: int
) -> tuple[bool, str | None]:
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=tg_user_id)
        return _is_member(member.status), None
    except TelegramBadRequest as exc:
        logging.warning("BadRequest on get_chat_member: %s", exc)
        return False, "bad_request"
    except TelegramAPIError as exc:
        logging.warning("TelegramAPIError on get_chat_member: %s", exc)
        return False, "api_error"




